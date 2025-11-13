from astro_pi_orbit import ISS
from datetime import UTC, datetime
from skyfield.api import load

iss = ISS()
time_scale = load.timescale()
time = datetime.now(UTC)
position = iss.at(time_scale.from_datetime(time))
# print(iss.coordinates(), position.km)
dir(position)