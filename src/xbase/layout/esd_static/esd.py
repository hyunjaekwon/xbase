from typing import Optional, Type, Any, Mapping

from bag.layout.template import TemplateBase, TemplateDB
from bag.layout.routing.base import WDictType, SpDictType, TrackManager
from bag.design.module import Module
from bag.util.immutable import Param

from pybag.core import BBox, Transform
from pybag.enum import Orientation

from . import ESDStatic
from ...schematic.esd import xbase__esd


class ESD(TemplateBase):
    """This class instantiates esd_vdd and esd_vss to make one complete unit ESD."""
    def __init__(self, temp_db: TemplateDB, params: Param, **kwargs: Any) -> None:
        TemplateBase.__init__(self, temp_db, params, **kwargs)
        self._conn_layer = -1
        self._tr_manager = None

    @property
    def conn_layer(self) -> int:
        return self._conn_layer

    @property
    def tr_manager(self) -> TrackManager:
        return self._tr_manager

    @classmethod
    def get_schematic_class(cls) -> Optional[Type[Module]]:
        return xbase__esd

    @classmethod
    def get_params_info(cls) -> Mapping[str, str]:
        return dict(
            esd_p='library name and cell name for esd_p.',
            esd_n='library name and cell name for esd_n.',
            tr_widths='Track widths dictionary',
            tr_spaces='Track spaces dictionary',
        )

    def draw_layout(self) -> None:
        tr_widths: WDictType = self.params['tr_widths']
        tr_spaces: SpDictType = self.params['tr_spaces']
        esd_p: Mapping[str, Any] = self.params['esd_p']
        esd_n: Mapping[str, Any] = self.params['esd_n']
        self._tr_manager = TrackManager(self.grid, tr_widths, tr_spaces)

        # make masters
        esd_p_master: ESDStatic = self.new_template(ESDStatic, params=dict(tr_widths=tr_widths, tr_spaces=tr_spaces,
                                                                           **esd_p))
        esd_p_bbox = esd_p_master.bound_box
        esd_n_master: ESDStatic = self.new_template(ESDStatic, params=dict(tr_widths=tr_widths, tr_spaces=tr_spaces,
                                                                           **esd_n))
        esd_n_bbox = esd_n_master.bound_box

        # Assume one unit ESD will have one esd_p and one esd_n. Generator can be extended to have programmable
        # number of esd_p and esd_n.

        tot_w = max(esd_p_bbox.w, esd_n_bbox.w)
        tot_h = esd_p_bbox.h + esd_n_bbox.h
        self._conn_layer = conn_layer = esd_p_master.conn_layer
        assert conn_layer == esd_n_master.conn_layer

        # add instances
        off_n = (tot_w - esd_n_bbox.w) // 2
        inst_n = self.add_instance(esd_n_master, inst_name='XN', xform=Transform(dx=off_n))
        off_p = (tot_w - esd_p_bbox.w) // 2
        inst_p = self.add_instance(esd_p_master, inst_name='XP', xform=Transform(dx=off_p, dy=tot_h,
                                                                                 mode=Orientation.MX))

        self.set_size_from_bound_box(conn_layer, BBox(0, 0, tot_w, tot_h), round_up=True)

        # --- Routing --- #
        vdd_n = inst_n.get_pin('VDD')
        vss_n = inst_n.get_pin('plus')
        term_n = inst_n.get_pin('minus')

        vdd_p = inst_p.get_pin('minus')
        vss_p = inst_p.get_pin('VSS')
        term_p = inst_p.get_pin('plus')

        for port_p, port_n, name in [(vdd_p, vdd_n, 'VDD'), (vss_p, vss_n, 'VSS'), (term_p, term_n, 'term')]:
            assert port_p.track_id.base_index == port_n.track_id.base_index
            self.add_pin(name, self.connect_wires([port_p, port_n]))

        # set schematic parameters
        self.sch_params = dict(
            esd_p=esd_p_master.sch_params,
            esd_n=esd_n_master.sch_params,
        )
