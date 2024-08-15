import pandas as pd
import matplotlib.pyplot as plt

# Read the CSV file
df = pd.read_csv('schlussgang_portraits_663.csv')

# Function to generate statistics for categorical data
def categorical_stats(column):
    if column in ['jetziger Beruf', 'gelernter Beruf', 'Lieblingsgetränk']:
        # Split multiple jobs and count each separately
        all_jobs = [job.strip() for jobs in df[column].dropna() for job in jobs.split('/')]
        counts = pd.Series(all_jobs).value_counts()
        percentages = counts / len(all_jobs) * 100
    else:
        counts = df[column].value_counts()
        percentages = df[column].value_counts(normalize=True) * 100
    
    stats = pd.concat([counts, percentages], axis=1, keys=['Count', 'Percentage'])
    stats['Percentage'] = stats['Percentage'].round(2)
    return stats

# Function to generate statistics for numerical data
def numerical_stats(column):
    stats = df[column].describe()
    return stats

def add_value_labels(ax, spacing=5):
    for rect in ax.patches:
        y_value = rect.get_height()
        x_value = rect.get_x() + rect.get_width() / 2
        label = f"{int(y_value)}"
        ax.annotate(label, (x_value, y_value), xytext=(0, spacing),
                    textcoords="offset points", ha='center', va='bottom')

# Generate and print statistics for each category
categories = ['jetziger Beruf', 'erlernter Beruf', 'Schuhgrösse', 'Lieblingsgetränk', 'Grösse (cm)', 'Gewicht (kg)']

for category in categories:
    print(f"\nStatistics for {category}:")
    if df[category].dtype == 'object':
        print(categorical_stats(category))
    else:
        print(numerical_stats(category))

    # Generate a bar plot for categorical data or a histogram for numerical data
    fig, ax = plt.subplots(figsize=(14, 8))
    if df[category].dtype == 'object':
        if category in ['jetziger Beruf', 'erlernter Beruf', 'Lieblingsgetränk']:
            all_jobs = [job.strip() for jobs in df[category].dropna() for job in jobs.split('/')]
            top_15 = pd.Series(all_jobs).value_counts().nlargest(15)
            top_15.plot(kind='bar', ax=ax)
        else:
            df[category].value_counts().plot(kind='bar', ax=ax)
        add_value_labels(ax)
        ax.set_title(f"Distribution of {category}")
        ax.set_xlabel(category)
        ax.set_ylabel("Count")
    else:
        df[category].hist(bins=20, ax=ax)
        ax.set_title(f"Distribution of {category}")
        ax.set_xlabel(category)
        ax.set_ylabel("Frequency")
    
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(f"{category.replace(' ', '_')}_distribution.png", dpi=300, bbox_inches='tight')
    plt.close(fig)

print("\nPlots have been saved as PNG files.")