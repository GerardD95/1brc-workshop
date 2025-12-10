import sys
import csv
import time
import multiprocessing

# refferd to this blog when implementing the solution: https://medium.com/@codingguy/the-1-billion-rows-challenge-django-cb689721baef

class WeatherStationStats:
    """
        Class to hold weather station statistics
    """
    def __init__(self, min_temp=float('inf'), max_temp=float('-inf'), sum_temp=0, count=0):
        self.min = min_temp
        self.max = max_temp
        self.sum = sum_temp
        self.count = count


def process_chunk(chunk):
    """
    Process a chunk of measurement data and return aggregated statistics.
    
    Args:
        chunk: List of rows where each row is [station_name, temperature]
    
    Returns:
        dict: Dictionary with station names as keys and WeatherStationStats as values
    """
    weather_data = {}

    for row in chunk:
        station, temp = row
        temp = int(float(temp) * 10)

        if station not in weather_data:
            weather_data[station] = WeatherStationStats(float('inf'), float('-inf'), 0, 0)
        
        station_stats = weather_data[station]
        station_stats.min = min(station_stats.min, temp)
        station_stats.max = max(station_stats.max, temp)
        station_stats.sum += temp
        station_stats.count += 1

    return weather_data


def print_measurements(cities: dict) -> None:
    """
    Print temperature measurements for cities in a formatted output.
    This function takes a dictionary of cities and their temperature measurements,
    then outputs the minimum, mean, and maximum temperatures for each city in 
    alphabetical order.

    NOTE: This function MUST print to stdout to be compatible with leaderboard.py
    which checks the results and measures runtime performance.

    Args:
        cities (dict): A dictionary where keys are city names (str) and values
                      contain temperature measurement data. The exact structure
                      of the values depends on how measurements are stored
                      (e.g., list of floats, measurement objects, etc.).
    Returns:
        None: This function prints directly to stdout and does not return a value.
    Output Format:
        Each city is printed on a separate line with the format:
        {city_name}={min_temp}/{mean_temp}/{max_temp}
        - All temperatures are formatted to exactly one decimal place
        - Temperature values range from -99.9 to 99.9 degrees
        - Cities are sorted alphabetically by name
        - Mean temperature is calculated as the arithmetic average
    Example:
        >>> cities_data = {
        ...     "Berlin": [10.2, -5.8, 23.1, 8.7],
        ...     "Amsterdam": [12.4, 8.9, 16.7, 11.2]
        ... }
        >>> print_measurements(cities_data)
        Amsterdam=8.9/12.3/16.7
        Berlin=-5.8/9.1/23.1
    """
    # Pre-sort cities once instead of sorting on each iteration
    sorted_cities = sorted(cities.keys())
    
    for city in sorted_cities:
        min_temp, mean_temp, max_temp = cities[city]
        print(f"{city}={min_temp:.1f}/{mean_temp:.1f}/{max_temp:.1f}")

    

def main(measurements_file_path: str) -> dict:
    """
    Process temperature measurements from a file and return aggregated statistics.
    Args:
        measurements_file_path (str): Path to the file containing temperature measurements.
    Returns:
        dict: Dictionary with station names and temperature measurements/ statistics.
    """
    # Create a multiprocessing pool with all available CPU cores
    pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())

    # Read the file and split into chunks
    with open(measurements_file_path, newline='', encoding='utf-8') as file:
        reader = csv.reader(file, delimiter=';')
        chunks = []
        chunk_size = 100000
        chunk = []

        for row in reader:
            chunk.append(row)
            if len(chunk) >= chunk_size:
                chunks.append(chunk)
                chunk = []

        # Add remaining rows as the last chunk
        if chunk:
            chunks.append(chunk)

    # Process chunks in parallel
    results = pool.map(process_chunk, chunks)
    pool.close()
    pool.join()

    # Merge results from all chunks
    final_weather_data = {}
    for weather_data in results:
        for station, stats in weather_data.items():
            if station not in final_weather_data:
                final_weather_data[station] = WeatherStationStats(float('inf'), float('-inf'), 0, 0)
            
            final_stats = final_weather_data[station]
            final_stats.min = min(final_stats.min, stats.min)
            final_stats.max = max(final_stats.max, stats.max)
            final_stats.sum += stats.sum
            final_stats.count += stats.count

    # Convert to final format: {station: (min, mean, max)}
    result = {
        station: (stats.min, stats.sum / stats.count, stats.max) 
        for station, stats in final_weather_data.items()
    }
    return result


if __name__ == '__main__':
    cities = main(sys.argv[1])
    print_measurements(cities)