import matplotlib.pyplot as plt

def plot_results(total_reward, avg_reward, results, clicks, dups):
    
    fig1, ax1 = plt.subplots()
    ax1.set_xlabel('Episode #')
    ax1.set_ylabel('Episode Reward (Circle)')
    
    ax2 = ax1.twinx()
    ax2.set_ylabel('Mean Episode Reward (Triangle)')
    
    fig1.tight_layout()
    
    fig2, ax3 = plt.subplots()
    ax3.set_xlabel('Episode #')
    ax3.set_ylabel('Number of Clicks')
    ax3.set_ylim([0, max(clicks)*1.1])
    
    ax4 = ax3.twinx()
    ax4.set_ylabel('Number of Dup. Values')
    
    for i in range(len(results)):
        if results[i] == "W":
            icon = "g"
        else:
            icon = "r"
        
        ax1.plot(i, total_reward[i], icon+"o")
        ax2.plot(i, avg_reward[i], icon+"v")
        
        ax3.plot(i, clicks[i], icon+"o")
        ax4.plot(i, dups[i])

    
    plt.show()


if __name__ == "__main__":
    ep_rewards = [-569.000, -298.000, -164.000, -194.000]
    avg_rewards = [-8.754, -10.643, -10.250, -10.211]
    result = ["L", "L", "L", "L"]
    clicks = [10, 4, 5, 5]
    
    plot_results(ep_rewards, avg_rewards, result, clicks)