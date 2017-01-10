import logging
l = logging.getLogger('simuvex.s_unicorn')

from ..engines import SimEngine

#pylint: disable=arguments-differ

class SimEngineUnicorn(SimEngine):
    """
    Concrete exection in the Unicorn Engine, a fork of qemu.
    """
    def __init__(self, base_stop_points=None):
        self.base_stop_points = base_stop_points

    def process(self, state,
            step=None,
            extra_stop_points=None,
            inline=False,
            force_addr=None,
            **kwargs):
        """
        :param state:               The state with which to execute
        :param step:                How many basic blocks we want to execute
        :param extra_stop_points:   A collection of addresses at which execution should halt
        :param inline:              This is an inline execution. Do not bother copying the state.
        :param force_addr:          Force execution to pretend that we're working at this concrete
                                    address
        :returns:                   A SimSuccessors object categorizing the results of the run and
                                    whether it succeeded.
        """
        return super(SimEngineUnicorn, self).process(state,
                step=step,
                extra_stop_points=extra_stop_points,
                inline=inline,
                force_addr=force_addr)

    def _process(self, state, successors, step, extra_stop_points):
        if o.UNICORN not in state.options or not state.unicorn.check():
            return
        if extra_stop_points is None:
            extra_stop_points = set(self.base_stop_points)
        else:
            # convert extra_stop_points to a set
            if not isinstance(extra_stop_points, set):
                extra_stop_points = set(extra_stop_points)
            extra_stop_points.update(self.base_stop_points)
        if successors.addr in extra_stop_points:
            return  # trying to start unicorn execution on a stop point

        successors.sort = 'Unicorn'

        # initialize unicorn plugin
        state.unicorn.setup()
        try:
            state.unicorn.set_stops(extra_stop_points)
            state.unicorn.hook()
            state.unicorn.start(step=step)
            state.unicorn.finish()
        finally:
            state.unicorn.destroy()

        if state.unicorn.errno:
            # error from unicorn
            #err = str(unicorn.UcError(state.unicorn.errno))
            successors.initial_state.unicorn.countdown_symbolic_memory = state.unicorn.countdown_symbolic_memory
            successors.initial_state.unicorn.countdown_symbolic_registers = state.unicorn.countdown_symbolic_registers
            successors.initial_state.unicorn.countdown_nonunicorn_blocks = state.unicorn.countdown_nonunicorn_blocks
            return
        elif state.unicorn.steps == 0:
            successors.initial_state.unicorn.countdown_symbolic_memory = state.unicorn.countdown_symbolic_memory
            successors.initial_state.unicorn.countdown_symbolic_registers = state.unicorn.countdown_symbolic_registers
            successors.initial_state.unicorn.countdown_nonunicorn_blocks = state.unicorn.countdown_nonunicorn_blocks
            return

        state.scratch.executed_block_count += state.unicorn.steps

        if state.unicorn.jumpkind.startswith('Ijk_Sys'):
            state.ip = state.unicorn._syscall_pc
        successors.add_successor(state, state.ip, state.se.true, state.unicorn.jumpkind)

        successors.description = 'Unicorn (%s after %d steps)' % (STOP.name_stop(state.unicorn.stop_reason), state.unicorn.steps)
        successors.processed = True

from ..plugins.unicorn_engine import STOP
from .. import s_options as o
