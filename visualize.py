import sys
import pickle
import matplotlib.pyplot as plt

def draw_all_eps_lst():
    if len(sys.argv) > 1:
        saving_dir = sys.argv[1]
    else:
        saving_dir = 'result.pkl'

    with open(saving_dir, 'rb') as handle:
        saving_dict = pickle.load(handle)

    all_eps_lst = saving_dict['all_eps_lst']

    num_eps_lst = [x for x in range(1,len(all_eps_lst)+1)]
    threshold_list = [all_eps_lst[-1]]*len(all_eps_lst)

    plt.plot(num_eps_lst, all_eps_lst, 'b-', num_eps_lst, threshold_list, 'y-')
    plt.axis([0, len(all_eps_lst)+1, 0, 0.6])
    plt.xlabel('Experiment Number')
    plt.ylabel('Eps')
    plt.show()

draw_all_eps_lst()