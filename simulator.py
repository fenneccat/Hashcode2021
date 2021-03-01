from TrafficPreprocessor import Graph
from collections import deque

class SimulationReport:
    def __init__(self):
        self.score = 0
        self.intersection_dict = {}

    def output(self):
        print("Score: ", self.score)
        print("Inefficient intersections and their inefficiencies: ", self.intersection_dict)

    def add_score(self, score):
        self.score += score

    def add_inefficient_intersection_count(self, intersection):
        if intersection not in self.intersection_dict:
            self.intersection_dict[intersection] = 0
        self.intersection_dict[intersection] += 1

class LightState:
    def __init__(self, dict_intersection_to_dict_street_to_ison):
        self.dict_intersection_to_dict_street_to_ison = dict_intersection_to_dict_street_to_ison

    def is_on(self, intersection, street) -> bool:
        assert(intersection in self.dict_intersection_to_dict_street_to_ison)
        street_to_state = self.dict_intersection_to_dict_street_to_ison[intersection]
        assert(street in street_to_state)
        return street_to_state[street]

    def get_greenlighted_street(self, intersection) -> int:
        assert(intersection in self.dict_intersection_to_dict_street_to_ison)
        street_to_state = self.dict_intersection_to_dict_street_to_ison[intersection]
        for street in street_to_state:
            is_on = street_to_state[street]
            if is_on:
                return street
        assert(False)
        return -1


class LightSchedule:
    def __init__(self, dict_intersection_to_streets):
        self.dict_intersection_to_street_and_period_list = {}
        for intersection in dict_intersection_to_streets:
            self.dict_intersection_to_street_and_period_list[intersection] = []
            streets = dict_intersection_to_streets[intersection]
            for street in streets:
                self.dict_intersection_to_street_and_period_list[intersection].append((street, 1))

    def get_state(self, t) -> LightState:
        dict = {}
        for intersection in self.dict_intersection_to_street_and_period_list:
            dict[intersection] = {}
            street_and_period_list = self.dict_intersection_to_street_and_period_list[intersection]
            total_period = self.get_total_period(intersection)
            t_remainder = t % total_period
            for street, period in street_and_period_list:
                if (t_remainder >= 0) and ((t_remainder-period) < 0):
                    dict[intersection][street] = True
                else:
                    dict[intersection][street] = False
                t_remainder -= period
        return LightState(dict)

    def get_total_period(self, intersection) -> int:
        street_and_period_list = self.dict_intersection_to_street_and_period_list[intersection]
        sum_period = 0
        for street, period in street_and_period_list:
            sum_period += period
        return sum_period

    def __str__(self):
        return str(self.dict_intersection_to_street_and_period_list)


class CarsState:
    def __init__(self, cars_and_their_initial_streets, street_map):
        self.car_state = cars_and_their_initial_streets
        self.street_map = street_map
        self.street_queued_state = dict()
        for car, street in self.car_state.items():
            self.street_queued_state.setdefault(street, deque([])).append(car)
        self.street_running_state = dict()

        print(self)

    def has_queued_car_on_street(self, street):
        return True if street in self.street_queued_state and len(self.street_queued_state[street]) > 0 else False

    def update(self, car, next_street):
        print("updating")
        current_street = self.car_state[car]
        self.car_state[car] = next_street
        assert self.street_queued_state[current_street][0] == car
        self.street_queued_state[current_street].popleft()
        self.street_running_state.setdefault(next_street,[]).append((car, self.street_map.streets_length[next_street]))

    def peek_queue_on_street(self, street):
        if street in self.street_queued_state:
            return self.street_queued_state[street][0]
        return None

    def advance_not_queued_cars(self):
        print("advancing")
        for street in range(self.street_map.num_street):
            new_street = []
            if street not in self.street_running_state: continue
            for car in self.street_running_state[street]:
                if car[1] > 0:
                    new_street.append((car[0], car[1] - 1))
                    if car[1] == 1:
                        del self.street_running_state[street]
                        self.street_queued_state.setdefault(street,deque([])).append(car[0])
            self.street_running_state[street] = new_street

    def remove(self, car):
        self.car_state[car] = -1

    def has_queued_car_on_intersection(self, intersection):
        if intersection not in self.street_map.incoming_streets: return False
        return any(
            [self.has_queued_car_on_street(street) for street in self.street_map.get_incoming_streets(intersection)])

    def get_queued_cars_and_streets(self):
        queued_cars_and_streets = []
        for street in range(self.street_map.num_street):
            if street not in self.street_queued_state: continue
            for car in self.street_queued_state[street]:
                queued_cars_and_streets.append((car, street))

        return queued_cars_and_streets

    def __str__(self):
        return "car_state: " + str(self.car_state) + " street_running_state: " +  str(self.street_running_state) + \
            " queued_state: " + str(self.street_queued_state)


class CarTravels:
    def __init__(self, dict_car_to_streets):
        self.dict_car_to_streets = dict_car_to_streets

    def get_next_street_of(self, car, street):
        streets = self.dict_car_to_streets[car]
        found = False
        for current_street in streets:
            if found:
                return current_street
            if current_street == street:
                found = True
        assert(False)


    def is_last_street(self, car, street):
        return self.dict_car_to_streets[car][-1] == street




class Simulator:
    def __init__(self, graph:Graph, car_travels:CarTravels, cars_initial_streets, finish_bonus:int):
        self.graph = graph
        self.car_travels = car_travels
        self.cars_initial_streets = cars_initial_streets
        self.finish_bonus = finish_bonus
        pass

    def simulate(self, duration:int, light_schedule: LightSchedule) -> SimulationReport:
        print(light_schedule)
        cars_state = CarsState(self.cars_initial_streets, self.graph)
        score = 0
        report = SimulationReport()
        for t in range(1, duration+1):
            print(t)
            lights_state = light_schedule.get_state(t)
            cars_state = self.update_cars_and_record_inefficient_intersections(cars_state, lights_state, report)
            num_removed_cars = self.remove_finished_cars(cars_state)
            score += num_removed_cars * (self.finish_bonus + (duration - t))
            print(cars_state)
        report.add_score(score)

        return report

    def update_cars_and_record_inefficient_intersections(self, cars_state:CarsState, lights_state:LightState, report:SimulationReport) -> CarsState:
        intersections = self.graph.get_intersections()
        queued_cars_and_next_street = []
        for intersection in intersections:
            greenlighted_street = lights_state.get_greenlighted_street(intersection)
            if cars_state.has_queued_car_on_street(greenlighted_street):
                car = cars_state.peek_queue_on_street(greenlighted_street)
                next_street = self.car_travels.get_next_street_of(car, greenlighted_street)
                queued_cars_and_next_street.append((car, next_street))

            elif cars_state.has_queued_car_on_intersection(intersection):
                # inefficient
                report.add_inefficient_intersection_count(intersection)
        cars_state.advance_not_queued_cars()
        for car, next_street in queued_cars_and_next_street:
            cars_state.update(car, next_street)
        return cars_state


    def remove_finished_cars(self, cars_state: CarsState) -> int:
        cars = cars_state.get_queued_cars_and_streets()
        remove_count = 0
        for car, street in cars:
            if self.car_travels.is_last_street(car, street):
                cars_state.remove(car)
                remove_count += 1
        return remove_count
