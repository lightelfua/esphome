import esphome.codegen as cg
import esphome.config_validation as cv
from esphome import automation
from esphome.components.image import Image_
from esphome.const import CONF_DURATION, CONF_ID
from esphome.core import ID
from .codegen import action_to_code
from .defines import (
    CONF_ANIMIMG,
    CONF_REPEAT_COUNT,
    CONF_AUTO_START,
    CONF_SRC,
    CONF_LABEL,
    CONF_IMG,
)
from .lv_validation import lv_repeat_count, lv_milliseconds
from .types import ObjUpdateAction, lv_animimg_t, void_ptr
from .widget import get_widget, Widget, WidgetType

ANIMIMG_BASE_SCHEMA = cv.Schema(
    {
        cv.Optional(CONF_REPEAT_COUNT, default="forever"): lv_repeat_count,
        cv.Optional(CONF_AUTO_START, default=True): cv.boolean,
    }
)
ANIMIMG_SCHEMA = ANIMIMG_BASE_SCHEMA.extend(
    {
        cv.Required(CONF_DURATION): lv_milliseconds,
        cv.Required(CONF_SRC): cv.ensure_list(cv.use_id(Image_)),
    }
)

ANIMIMG_MODIFY_SCHEMA = ANIMIMG_BASE_SCHEMA.extend(
    {
        cv.Optional(CONF_DURATION): lv_milliseconds,
    }
)


class AnimimgType(WidgetType):
    def __init__(self):
        super().__init__(CONF_ANIMIMG, ANIMIMG_SCHEMA, ANIMIMG_MODIFY_SCHEMA)

    @property
    def w_type(self):
        return lv_animimg_t

    async def to_code(self, w: Widget, config):
        init = []
        wid = config[CONF_ID]
        if CONF_SRC in config:
            srcs = (
                "{" + ",".join([f"lv_img_from({x.id})" for x in config[CONF_SRC]]) + "}"
            )
            src_id = ID(f"{wid}_src", is_declaration=True, type=void_ptr)
            src_arry = cg.static_const_array(src_id, cg.RawExpression(srcs))
            count = len(config[CONF_SRC])
            init.append(f"lv_animimg_set_src({wid}, {src_arry}, {count})")
        init.extend(w.set_property(CONF_REPEAT_COUNT, config))
        init.extend(w.set_property(CONF_DURATION, config))
        if config.get(CONF_AUTO_START):
            init.append(f"lv_animimg_start({w.obj})")
        return init

    def get_uses(self):
        return CONF_IMG, CONF_LABEL


animimg_spec = AnimimgType()


@automation.register_action(
    "lvgl.animimg.start",
    ObjUpdateAction,
    cv.maybe_simple_value(
        {
            cv.Required(CONF_ID): cv.use_id(lv_animimg_t),
        },
        key=CONF_ID,
    ),
)
async def animimg_start(config, action_id, template_arg, args):
    widget = await get_widget(config[CONF_ID])
    init = [f"lv_animimg_start({widget.obj})"]
    return await action_to_code(init, action_id, widget, template_arg, args)


@automation.register_action(
    "lvgl.animimg.stop",
    ObjUpdateAction,
    cv.maybe_simple_value(
        {
            cv.Required(CONF_ID): cv.use_id(lv_animimg_t),
        },
        key=CONF_ID,
    ),
)
async def animimg_stop(config, action_id, template_arg, args):
    widget = await get_widget(config[CONF_ID])
    init = [f"lv_animimg_stop({widget.obj})"]
    return await action_to_code(init, action_id, widget, template_arg, args)
