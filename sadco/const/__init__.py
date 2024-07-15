from enum import Enum


class SurveyType(str, Enum):
    """Survey Types."""
    HYDRO = 'hydro'
    CURRENTS = 'currents'
    WEATHER = 'weather'
    WAVES = 'waves'
    ECHOSOUNDING = 'echo-sounding'
    UTR = 'utr'
    VOS = 'vos'
    UNKNOWN = 'unknown'


class DataType(str, Enum):
    """Data Types."""
    WATER = 'water'
    WATERCHEMISTRY = 'water_chemistry'
    WATERPOLLUTION = 'water_pollution'
    WATERNUTRIENTS = 'water_nutrients'
    WATERCURRENTS = 'water_currents'
    SEDIMENT = 'sediment'
    SEDIMENTCHEMISTRY = 'sediment_chemistry'
    SEDIMENTPOLLUTION = 'sediment_pollution'
    WATERNUTRIENTSANDCHEMISTRY = 'water_nutrients_and_chemistry'
    WEATHER = 'weather'
    CURRENTS = 'currents'


class SADCOScope(str, Enum):
    """Auth Scopes."""
    SURVEYS_READ = 'sadco.surveys:read'
    HYDRO_READ = 'sadco.hydro:read'
    CURRENTS_READ = 'sadco.currents:read'
    WEATHER_READ = 'sadco.weather:read'
    WAVES_READ = 'sadco.waves:read'
    ECHO_SOUNDING_READ = 'sadco.echo-sounding:read'
    UTR_READ = 'sadco.utr:read'
    HYDRO_DOWNLOAD = 'sadco.hydro:download'
    CURRENTS_DOWNLOAD = 'sadco.currents:download'
    WEATHER_DOWNLOAD = 'sadco.weather:download'
    WAVES_DOWNLOAD = 'sadco.waves:download'
    UTR_DOWNLOAD = 'sadco.utr:download'
    UNKNOWN_READ = 'sadco.unknown:read'
