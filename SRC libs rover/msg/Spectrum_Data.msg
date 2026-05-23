# Raw spectral data from LIBS sensor
std_msgs/Header header

# Wavelengths in nanometers (nm)
float64[] wavelengths

# Measured intensity values (relative units)
float64[] intensities

# Identifier for the sample being measured
string sample_id

# Integration time in seconds
float64 integration_time
