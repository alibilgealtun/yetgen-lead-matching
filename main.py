import pandas as pd
from pyairtable import Api, Base
from sklearn.cluster import KMeans
from sklearn.preprocessing import LabelEncoder
import numpy as np
from keys import api_key, base_id, table_name


def fetch_data(api_key, base_id, table_name):
    """
    Fetches data from Airtable using the provided API key, base ID, and table name.

    Args:
    - api_key (str): API key for Airtable authentication.
    - base_id (str): ID of the base in Airtable.
    - table_name (str): Name of the table in Airtable.

    Returns:
    - pd.DataFrame: DataFrame containing the fetched data.
    """
    try:
        api = Api(api_key)
        base = Base(api, base_id)
        table = base.table(table_name)
        records = table.all()
        data = []
        for record in records:
            fields = record['fields']
            data.append([
                fields.get('id'),
                fields.get('first_name'),
                fields.get('last_name'),
                fields.get('email'),
                fields.get('gender'),
                fields.get('university'),
                fields.get('city')
            ])
        return pd.DataFrame(data, columns=['id', 'first_name', 'last_name', 'email', 'gender', 'university', 'city'])
    except Exception as e:
        print(f"Error fetching data from Airtable: {e}")
        return pd.DataFrame()


def balance_clusters(data, cluster_col, target_size):
    """
    Balances clusters based on the given column and target size.

    Args:
    - data (pd.DataFrame): DataFrame containing the data to be balanced.
    - cluster_col (str): Column name on which clustering is based.
    - target_size (int): Target size for each balanced cluster.

    Returns:
    - pd.DataFrame: DataFrame with balanced clusters.
    """
    try:
        clusters = data[cluster_col].unique()
        balanced_data = pd.DataFrame(columns=data.columns)
        remaining_data = data.copy()

        for cluster in clusters:
            cluster_data = data[data[cluster_col] == cluster]
            if len(cluster_data) >= target_size:
                sampled_data = cluster_data.sample(target_size)
                balanced_data = pd.concat([balanced_data, sampled_data])
                remaining_data = remaining_data.drop(sampled_data.index)
            else:
                balanced_data = pd.concat([balanced_data, cluster_data])
                remaining_data = remaining_data.drop(cluster_data.index)

        # Ensure every group has exactly target_size members
        while len(balanced_data) % target_size != 0:
            additional_data = remaining_data.sample(1)
            balanced_data = pd.concat([balanced_data, additional_data])
            remaining_data = remaining_data.drop(additional_data.index)

        balanced_data.reset_index(drop=True, inplace=True)
        balanced_data['balanced_cluster'] = np.repeat(np.arange(len(balanced_data) // target_size), target_size)

        # Create new clusters from remaining students
        if not remaining_data.empty:
            remaining_cluster_count = (len(remaining_data) // target_size) + 1
            remaining_data['balanced_cluster'] = np.repeat(
                np.arange(balanced_data['balanced_cluster'].max() + 1,
                          balanced_data['balanced_cluster'].max() + 1 + remaining_cluster_count),
                target_size
            )[:len(remaining_data)]
            balanced_data = pd.concat([balanced_data, remaining_data])

        return balanced_data

    except Exception as e:
        print(f"Error balancing clusters: {e}")
        return pd.DataFrame()


def main():
    """
    Main function to execute data fetching, clustering, balancing, and saving to Excel.
    """
    try:
        # Fetch data from Airtable
        data = fetch_data(api_key, base_id, table_name)

        # Encode categorical data
        data_encoded = data.copy()
        le_gender = LabelEncoder()
        data_encoded['gender'] = le_gender.fit_transform(data['gender'])
        le_university = LabelEncoder()
        data_encoded['university'] = le_university.fit_transform(data['university'])
        le_city = LabelEncoder()
        data_encoded['city'] = le_city.fit_transform(data['city'])

        # Apply KMeans clustering
        num_clusters = 50  # Number of clusters
        kmeans = KMeans(n_clusters=num_clusters, random_state=42)
        data['cluster'] = kmeans.fit_predict(data_encoded[['gender', 'university', 'city']])

        # Balance clusters
        balanced_data = balance_clusters(data, 'cluster', 20)

        # Save grouped data to Excel
        grouped = balanced_data.groupby('balanced_cluster')
        with pd.ExcelWriter('grouped_data.xlsx') as writer:
            for cluster_id, group in grouped:
                group.to_excel(writer, sheet_name=f'Group_{cluster_id}', index=False)

    except Exception as e:
        print(f"Error in main function: {e}")


if __name__ == "__main__":
    main()
