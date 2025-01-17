import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components.sensor import (
    sensor_schema,
    Sensor,
    new_sensor,
)
from .. import (
    add_init_lambda,
    LVGL_SCHEMA,
)
from ..defines import CONF_WIDGET, CONF_LVGL_ID
from ..lv_validation import requires_component
from ..types import LvNumber
from ..widget import get_widget, Widget

BASE_SCHEMA = sensor_schema(Sensor).extend(LVGL_SCHEMA)
CONFIG_SCHEMA = cv.All(
    BASE_SCHEMA.extend(
        {
            cv.Required(CONF_WIDGET): cv.use_id(LvNumber),
        }
    ),
    requires_component("sensor"),
)


async def to_code(config):
    sensor = await new_sensor(config)
    paren = await cg.get_variable(config[CONF_LVGL_ID])
    widget = await get_widget(config[CONF_WIDGET])
    assert isinstance(widget, Widget)
    init = widget.set_event_cb(
        f"{sensor}->publish_state({widget.get_value()});", "LV_EVENT_VALUE_CHANGED"
    )
    await add_init_lambda(paren, init)
