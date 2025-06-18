import esphome.codegen as cg
import esphome.config_validation as cv
from esphome import pins
from esphome.const import CONF_ID
from esphome.core import coroutine_with_priority

DEPENDENCIES = ["esp32"]
CODEOWNERS = ["@stas-sl"]

i2s_ns = cg.esphome_ns.namespace("i2s")
I2SComponent = i2s_ns.class_("I2SComponent", cg.Component)

MULTI_CONF = True

CONF_WS_PIN = "ws_pin"
CONF_BCK_PIN = "bck_pin"
CONF_DIN_PIN = "din_pin"
CONF_DOUT_PIN = "dout_pin"
CONF_ADC_PIN = "adc_pin"
CONF_ADC_ATTEN = "adc_atten"
CONF_SAMPLE_RATE = "sample_rate"
CONF_BITS_PER_SAMPLE = "bits_per_sample"
CONF_DMA_BUF_COUNT = "dma_buf_count"
CONF_DMA_BUF_LEN = "dma_buf_len"
CONF_USE_APLL = "use_apll"
CONF_BITS_SHIFT = "bits_shift"
CONF_CHANNEL = "channel"


i2s_channel_fmt_t = cg.global_ns.enum("i2s_channel_fmt_t")
CHANNELS = {
    "left": i2s_channel_fmt_t.I2S_CHANNEL_FMT_ONLY_LEFT,
    "right": i2s_channel_fmt_t.I2S_CHANNEL_FMT_ONLY_RIGHT,
}

def validate_adc_pin(config):
    if "adc_pin" in config and any(k in config for k in ["ws_pin", "bck_pin", "din_pin", "dout_pin"]):
        raise cv.Invalid("Cannot use the ADC pin together with any other I2S pin")
    if "adc_pin" not in config and any(k in config for k in ["din_pin", "dout_pin"]) and not all(k in config for k in ["ws_pin", "bck_pin"]):
        raise cv.Invalid("If either a DIN pin or a DOUT pin is defined, the WS pin and the BCK pin must also be defined")

    return config

CONFIG_SCHEMA = cv.All(
    cv.Schema(
        {
            cv.GenerateID(): cv.declare_id(I2SComponent),
            cv.Optional(CONF_WS_PIN): pins.internal_gpio_output_pin_schema,
            cv.Optional(CONF_BCK_PIN): pins.internal_gpio_output_pin_schema,
            cv.Optional(CONF_DIN_PIN): pins.internal_gpio_input_pin_schema,
            cv.Optional(CONF_DOUT_PIN): pins.internal_gpio_output_pin_schema,
            cv.Optional(CONF_ADC_PIN): pins.internal_gpio_input_pin_schema,
            cv.Optional(CONF_ADC_ATTEN, default="12db"): cv.one_of("0db", "2.5db", "6db", "12db"),
            cv.Optional(CONF_SAMPLE_RATE, 48000): cv.positive_not_null_int,
            cv.Optional(CONF_BITS_PER_SAMPLE, 32): cv.one_of(8, 16, 24, 32, int=True),
            cv.Optional(CONF_DMA_BUF_COUNT, 8): cv.positive_not_null_int,
            cv.Optional(CONF_DMA_BUF_LEN, 256): cv.positive_not_null_int,
            cv.Optional(CONF_USE_APLL, False): cv.boolean,
            cv.Optional(CONF_BITS_SHIFT, 0): cv.int_range(0, 32),
            cv.Optional(CONF_CHANNEL, default="right"): cv.enum(CHANNELS),
        }
    ).extend(cv.COMPONENT_SCHEMA),
    cv.has_at_least_one_key(CONF_DIN_PIN, CONF_DOUT_PIN, CONF_ADC_PIN),
    validate_adc_pin,
)


@coroutine_with_priority(1.0)
async def to_code(config):
    cg.add_global(i2s_ns.using)
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)
    if CONF_WS_PIN in config:
        ws_pin = await cg.gpio_pin_expression(config[CONF_WS_PIN])
        cg.add(var.set_ws_pin(ws_pin))
    if CONF_BCK_PIN in config:
        bck_pin = await cg.gpio_pin_expression(config[CONF_BCK_PIN])
        cg.add(var.set_bck_pin(bck_pin))
    if CONF_DIN_PIN in config:
        din_pin = await cg.gpio_pin_expression(config[CONF_DIN_PIN])
        cg.add(var.set_din_pin(din_pin))
    if CONF_DOUT_PIN in config:
        dout_pin = await cg.gpio_pin_expression(config[CONF_DOUT_PIN])
        cg.add(var.set_dout_pin(dout_pin))
    if CONF_ADC_PIN in config:
        adc_pin = await cg.gpio_pin_expression(config[CONF_ADC_PIN])
        cg.add(var.set_adc_pin(adc_pin))
    cg.add(var.set_sample_rate(config[CONF_SAMPLE_RATE]))
    cg.add(var.set_bits_per_sample(config[CONF_BITS_PER_SAMPLE]))
    cg.add(var.set_dma_buf_count(config[CONF_DMA_BUF_COUNT]))
    cg.add(var.set_dma_buf_len(config[CONF_DMA_BUF_LEN]))
    cg.add(var.set_use_apll(config[CONF_USE_APLL]))
    cg.add(var.set_bits_shift(config[CONF_BITS_SHIFT]))

    atten_map = {
        "0db": cg.global_ns.ADC_ATTEN_DB_0,
        "2.5db": cg.global_ns.ADC_ATTEN_DB_2_5,
        "6db": cg.global_ns.ADC_ATTEN_DB_6,
        "12db": cg.global_ns.ADC_ATTEN_DB_12,
    }
    if CONF_ADC_ATTEN in config:
        cg.add(var.set_adc_atten(atten_map[config[CONF_ADC_ATTEN]]))

    cg.add(var.set_channel(config[CONF_CHANNEL]))
