import numpy as np

class SpectrumGenerator:
    def __init__(self, database_config):
        """
        Initialize generator with spectral database configuration.
        """
        self.config = database_config
        self.wavelengths = np.linspace(200, 900, 2000) # 200-900nm with 0.35nm resolution
        
    def generate_spectrum(self, sample_type, noise_level=0.05):
        """
        Generate a synthetic spectrum for a given sample type.
        Returns: (wavelengths, intensities)
        """
        if sample_type not in self.config['samples']:
            raise ValueError(f"Unknown sample type: {sample_type}")
            
        sample_info = self.config['samples'][sample_type]
        elements = sample_info['elements']
        
        # Start with baseline random noise
        intensities = np.random.normal(0.1, noise_level, len(self.wavelengths))
        intensities = np.abs(intensities) # Intensity must be positive
        
        # Add characteristic peaks for each element
        for elem in elements:
            symbol = elem['symbol']
            weight = elem['weight']
            
            if symbol in self.config['element_signatures']:
                peaks = self.config['element_signatures'][symbol]
                for peak_wavelength in peaks:
                    self._add_peak(intensities, peak_wavelength, weight)
        
        # Add some Bremsstrahlung background (continuum radiation)
        # Simple simulation: decay function
        continuum = 0.2 * np.exp(-(self.wavelengths - 200) / 200)
        intensities += continuum
        
        # Normalize to 0-1 range (optional, but good for relative intensity)
        intensities = intensities / np.max(intensities)
        
        return self.wavelengths, intensities
        
    def _add_peak(self, intensities, center_wavelength, weight, width=1.0):
        """
        Add a Gaussian peak to the intensity array.
        """
        # Create Gaussian peak
        peak = weight * np.exp(-0.5 * ((self.wavelengths - center_wavelength) / width) ** 2)
        intensities += peak
