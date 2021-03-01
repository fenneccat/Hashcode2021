from simulator import Simulator, LightSchedule, SimulationReport, CarsState, CarTravels
from TrafficPreprocessor import readTraffic, Graph

if __name__ == '__main__':
    D, I, S, V, F, street2idx, idx2street, cars_path, street_map = readTraffic("./a.txt")
    print(idx2street)

    car_travels = CarTravels(cars_path)
    light_schedule = LightSchedule(street_map.get_dict_intersection_to_streets())

    cars_and_their_initial_streets = dict()

    for car, path in cars_path.items():
        cars_and_their_initial_streets[car] = path[0]

    simulator = Simulator(street_map, car_travels, cars_and_their_initial_streets, F)
    report = simulator.simulate(D, light_schedule)
    report.output()