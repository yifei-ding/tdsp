import copy


class Formula(object):
    """
    the formula is either a linear function f = t(timestep) + coefficient * d(u,v)
    or f = const
    """

    def __init__(self, coefficient, weight, constant):
        self.intercept = 0
        self.coefficient = coefficient
        self.weight = weight
        self.constant = constant
        if self.constant == 0:
            self.isConst = False
            self.setIntercept()
        else:
            self.isConst = True

    def eval(self, timestep):
        if self.isConst:
            return self.constant
        else:
            return timestep + self.intercept

    def compose(self, next_formula):
        if self.isConst and not next_formula.isConst:
            return Formula([], [], self.constant + next_formula.intercept)
        elif next_formula.isConst:
            return copy.deepcopy(next_formula)
        else:
            new_coefficient = self.coefficient + next_formula.coefficient
            new_weight = self.weight + next_formula.weight
            return Formula(new_coefficient, new_weight, 0)

    def eval_reverse(self, y):
        assert (not self.isConst)
        return y - self.intercept

    def setIntercept(self):
        multiply = 0
        assert len(self.coefficient) == len(self.weight)
        for i in range(len(self.coefficient)):
            multiply += self.coefficient[i] * self.weight[i]
        self.intercept = int(multiply)  # TODO: check this

    def __repr__(self):
        if self.isConst:
            return f'f={self.constant}'
        else:
            return f'f=t+{self.intercept}'


def formula_parser(function_str, weight):
    if function_str.isalnum():
        return Formula([], [], int(function_str))
    else:
        coefficient = [float(''.join(function_str[1:]))]
        weight = [weight]
        return Formula(coefficient, weight, 0)


def calculate_function_reverse(function, weight, current_time):
    coefficient = float(''.join(function[1:]))
    return current_time - weight * coefficient


def merge(a, b):
    result = {}
    keys_list_b = list(sorted(b.keys()))
    i = 0
    for key in sorted(a.keys()):
        # calculate y at interval boarders
        print(f'key={key}')
        start_time = key[0]
        end_time = key[1]
        a_start = a[key].eval(start_time)
        a_end = a[key].eval(end_time)
        print(f'a_start={a_start}, a_end={a_end}')

        while i < len(keys_list_b):
            # find y1 y2 (a_start, a_end) falls into which interval of b
            b_start = keys_list_b[i][0]
            b_end = keys_list_b[i][1]
            print(f'b_start={b_start},b_end={b_end}')
            if b_start <= a_start < b_end < a_end:
                print(1)
                new_interval = (start_time, a[key].eval_reverse(b_end))
                result[new_interval] = a[key].compose(b[keys_list_b[i]])
                start_time = a[key].eval_reverse(b_end)  # TODO: verify
                # consume current interval and go to next b
                i += 1
            elif a_start <= b_start and a_end > b_end:
                print(2)
                # consume current interval and go to next b
                i += 1
            elif a_start <= b_start < a_end < b_end:
                print(3)
                new_interval = (a[key].eval_reverse(b_start), end_time)
                result[new_interval] = a[key].compose(b[keys_list_b[i]])
                break
            elif a_start >= b_start and a_end < b_end:
                print(4)
                new_interval = (start_time, end_time)
                result[new_interval] = a[key].compose(b[keys_list_b[i]])
                break
            else:
                print(5)
                break

    return result


def fifo(a):
    """from last interval, check the two neighbouring interval
    modify to FIFO
    """
    result = {}
    reversed_keys_list = list(reversed(list(a.keys())))
    last_interval = reversed_keys_list[0]
    # add the last interval directly
    result[last_interval] = copy.deepcopy(a[last_interval])
    for i, key in enumerate(reversed_keys_list):
        # calculate the result at interval boarders
        if i < len(reversed_keys_list) - 1:
            current_interval = reversed_keys_list[i]
            previous_interval = reversed_keys_list[i + 1]
            start_time_of_cur = current_interval[0]
            end_time_of_pre = previous_interval[1]
            # print(f'checking current={reversed_keys_list[i]}, pre={reversed_keys_list[i + 1]}',
            #       start_time_of_cur, end_time_of_pre)
            weight_of_cur_start = a[current_interval].eval(start_time_of_cur)
            weight_of_pre_end = a[previous_interval].eval(end_time_of_pre)
            if weight_of_pre_end <= weight_of_cur_start:
                result[previous_interval] = copy.deepcopy(a[previous_interval])
            else:
                start_time_of_pre = previous_interval[0]
                weight_of_pre_start = a[previous_interval].eval(start_time_of_pre)
                if weight_of_pre_start >= weight_of_cur_start:
                    result[previous_interval] = Formula([], [], (int(weight_of_cur_start)))
                else:
                    # split the previous interval into two. The first part is the same
                    # the second part equals to weight_of_cur_start
                    changing_timestep = a[previous_interval].eval_reverse(weight_of_cur_start)
                    result[(changing_timestep, end_time_of_pre)] = Formula([], [], (int(weight_of_cur_start)))
                    result[(start_time_of_pre, changing_timestep)] = copy.deepcopy(a[previous_interval])
    return result


if __name__ == "__main__":
    a = {(0, 20): "t+1", (20, 30): "t+1.2", (30, 40): "t+1"}
    b = {(0, 40): "t+1", (40, 100): "t+1.2"}
    weight_a = 10
    weight_b = 10
    for k, v in a.items():
        a[k] = formula_parser(v, weight_a)
    for k, v in b.items():
        b[k] = formula_parser(v, weight_b)

    a = fifo(a)
    b = fifo(b)
    print(f'After fifo: a={a} \n'
           f'b={b}')
    result = merge(a,b)
    print(result)
