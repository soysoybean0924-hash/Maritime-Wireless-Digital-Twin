"""Lightweight maritime evaporation-duct channel model for the twin API.

This module mirrors the browser demo at low computational cost. It is the first
backend anchor for the digital-twin loop: Three.js injects the current
environment and geometry, Python returns channel predictions.
"""

from __future__ import annotations

import math
import time
from dataclasses import dataclass
from typing import Any, Mapping


C = 3.0e8
EARTH_RADIUS_M = 6_371_000.0


@dataclass(frozen=True)
class Position:
    x: float
    y: float
    z: float

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any], default: "Position") -> "Position":
        return cls(
            x=float(value.get("x", default.x)),
            y=float(value.get("y", default.y)),
            z=float(value.get("z", default.z)),
        )

    def distance_to(self, other: "Position") -> float:
        return math.sqrt(
            (self.x - other.x) ** 2
            + (self.y - other.y) ** 2
            + (self.z - other.z) ** 2
        )


def _float(payload: Mapping[str, Any], key: str, default: float) -> float:
    try:
        return float(payload.get(key, default))
    except (TypeError, ValueError):
        return default


def _saturation_vapor_pressure(temp_c: float) -> float:
    return 6.112 * math.exp((17.67 * temp_c) / (temp_c + 243.5))


def _actual_vapor_pressure(temp_c: float, rh: float) -> float:
    return _saturation_vapor_pressure(temp_c) * rh / 100.0


def estimate_duct(payload: Mapping[str, Any]) -> dict[str, float | bool]:
    air_temp = _float(payload, "airTemp", 26.5)
    sea_temp = _float(payload, "seaTemp", 28.0)
    rh = _float(payload, "rh", 75.0)
    wind_speed = max(0.1, _float(payload, "windSpeed", 5.0))
    pressure = _float(payload, "pressure", 1013.25)
    astd = air_temp - sea_temp

    humidity_gap = max(
        0.0,
        _saturation_vapor_pressure(sea_temp)
        - _actual_vapor_pressure(air_temp, rh),
    )
    instability = max(0.0, sea_temp - air_temp)
    wind_factor = 1.0 / (1.0 + 0.08 * max(0.0, wind_speed - 3.0))
    vapor_score = min(1.0, humidity_gap / 14.0)
    instability_score = min(1.0, instability / 7.0)
    wind_score = max(0.0, 1.0 - abs(wind_speed - 5.0) / 15.0)
    duct_probability = max(
        0.0,
        min(0.98, 0.10 + 0.42 * vapor_score + 0.34 * instability_score + 0.14 * wind_score),
    )

    supplied_height = payload.get("ductHeight")
    if supplied_height is not None:
        duct_height = max(0.0, min(35.0, float(supplied_height)))
        duct_probability = max(duct_probability, min(0.98, duct_height / 35.0))
    else:
        duct_height = max(0.0, min(35.0, 1.8 * humidity_gap + 2.2 * instability * wind_factor))

    if duct_height > 0.01:
        surface_e = _saturation_vapor_pressure(sea_temp)
        air_e = _actual_vapor_pressure(air_temp, rh)
        t_air_k = air_temp + 273.15
        t_sea_k = sea_temp + 273.15
        n_surface = (77.6 / t_sea_k) * (pressure + (4810.0 * surface_e) / t_sea_k)
        n_air = (77.6 / t_air_k) * (pressure + (4810.0 * air_e) / t_air_k)
        duct_strength = abs((n_surface - n_air) + duct_height * 1e6 / EARTH_RADIUS_M)
        critical_freq = (100.0 / max(duct_height, 0.01) ** 1.5) * 1000.0
    else:
        duct_strength = 0.0
        critical_freq = math.inf

    return {
        "ductHeight": duct_height,
        "ductStrength": duct_strength,
        "criticalFreqMHz": critical_freq,
        "isTrapping": duct_height > 0.01,
        "ductProbability": duct_probability,
        "astd": astd,
    }


def predict_channel(payload: Mapping[str, Any]) -> dict[str, Any]:
    start = time.perf_counter()

    frequency_mhz = max(1.0, _float(payload, "frequency", 2600.0))
    tx_power = _float(payload, "txPower", 43.0)
    tx_gain = _float(payload, "txAntennaGain", 17.0)
    rx_gain = _float(payload, "rxAntennaGain", 10.0)
    tx_cable_loss = _float(payload, "txCableLoss", 3.0)
    rx_cable_loss = _float(payload, "rxCableLoss", 1.0)
    tx_height = max(0.1, _float(payload, "txHeight", 25.0))
    rx_height = max(0.1, _float(payload, "rxHeight", 3.0))

    base_default = Position(-210.5, 1.35, -58.0)
    boat_default = Position(25.0, 1.2, 20.0)
    base_pos = Position.from_mapping(payload.get("basePosition", {}), base_default)
    boat_pos = Position.from_mapping(payload.get("boatPosition", {}), boat_default)
    victim_default = Position(225.5, 1.35, -58.0)
    victim_pos = Position.from_mapping(payload.get("victimBasePosition", {}), victim_default)
    distance_m = max(0.5, base_pos.distance_to(boat_pos))
    victim_distance_m = max(0.5, base_pos.distance_to(victim_pos))

    wavelength = C / (frequency_mhz * 1e6)
    critical_distance = (4.0 * math.pi * tx_height * rx_height) / wavelength
    if distance_m < critical_distance:
        path_loss = 32.4 + 20.0 * math.log10(frequency_mhz) + 20.0 * math.log10(distance_m / 1000.0)
        base_model = "free-space"
    else:
        path_loss = (
            40.0 * math.log10(distance_m)
            - 20.0 * math.log10(tx_height)
            - 20.0 * math.log10(rx_height)
        )
        base_model = "two-ray"

    duct = estimate_duct(payload)
    duct_height = float(duct["ductHeight"])
    duct_strength = float(duct["ductStrength"])
    critical_freq = float(duct["criticalFreqMHz"])
    duct_probability = float(duct["ductProbability"])

    duct_gain = 0.0
    if duct_height > 0.01:
        tx_in_duct = max(0.0, 1.0 - tx_height / max(duct_height, 0.01))
        rx_in_duct = max(0.0, 1.0 - rx_height / max(duct_height, 0.01))
        height_factor = min(tx_in_duct, rx_in_duct)
        if frequency_mhz <= critical_freq:
            freq_factor = 1.0
        elif frequency_mhz <= critical_freq * 2.0:
            freq_factor = 1.0 - (frequency_mhz - critical_freq) / critical_freq * 0.5
        else:
            freq_factor = 0.25
        duct_gain = min(35.0, duct_strength * 2.5 * height_factor * max(0.0, freq_factor))

    effective_path_loss = path_loss - duct_gain
    eirp = tx_power + tx_gain - tx_cable_loss
    rx_power = eirp - effective_path_loss + rx_gain - rx_cable_loss

    direct_delay_us = distance_m / C * 1e6
    reflected_distance = math.sqrt(distance_m**2 + (tx_height + rx_height) ** 2)
    reflected_delay_us = reflected_distance / C * 1e6
    duct_delay_spread_us = 0.0
    if duct_height > 0.5:
        bounce_count = min(8.0, distance_m / max(duct_height * 5.0, 1.0))
        duct_delay_spread_us = bounce_count * duct_height * 2.0 / C * 1e6
    max_delay_us = max(reflected_delay_us, direct_delay_us + duct_delay_spread_us)

    inference_ms = (time.perf_counter() - start) * 1000.0
    model = "python-surrogate-duct" if duct_gain > 0.5 else f"python-surrogate-{base_model}"
    duct_exists = bool(duct["isTrapping"]) and duct_height > 0.5 and duct_probability >= 0.25
    victim_threshold_dbm = _float(payload, "victimInterferenceThresholdDbm", -94.0)
    victim_path_loss = 32.4 + 20.0 * math.log10(frequency_mhz) + 20.0 * math.log10(victim_distance_m / 1000.0)
    victim_duct_gain = duct_gain if duct_exists else 0.0
    interference_power = eirp - (victim_path_loss - victim_duct_gain) + rx_gain - rx_cable_loss
    interference_margin = interference_power - victim_threshold_dbm
    interference_alarm = duct_exists and interference_margin >= -6.0
    if not interference_alarm:
        interference_risk = "low"
    elif interference_margin >= 8.0 or duct_strength >= 9.0:
        interference_risk = "high"
    else:
        interference_risk = "medium"

    return {
        "model": model,
        "distanceM": round(distance_m, 3),
        "victimDistanceM": round(victim_distance_m, 3),
        "pathLossDb": round(effective_path_loss, 3),
        "rawPathLossDb": round(path_loss, 3),
        "ductGainDb": round(duct_gain, 3),
        "rxPowerDbm": round(rx_power, 3),
        "delayUs": round(max_delay_us, 3),
        "directDelayUs": round(direct_delay_us, 3),
        "ductExists": duct_exists,
        "ductProbability": round(duct_probability, 3),
        "ductHeightM": round(duct_height, 3),
        "ductStrengthMUnits": round(duct_strength, 3),
        "criticalFreqMHz": None if math.isinf(critical_freq) else round(critical_freq, 3),
        "interferenceAlarm": interference_alarm,
        "interferenceRisk": interference_risk,
        "interferencePowerDbm": round(interference_power, 3),
        "victimThresholdDbm": round(victim_threshold_dbm, 3),
        "interferenceMarginDb": round(interference_margin, 3),
        "interferenceReason": "duct_guided_cochannel_interference" if interference_alarm else "below_alarm_threshold",
        "astdC": round(float(duct["astd"]), 3),
        "inferenceMs": round(inference_ms, 3),
    }
