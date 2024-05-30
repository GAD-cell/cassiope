import json


def count_arxiv_and_years(file_path, output_file_path):
    # Initialisation des compteurs
    null_arxiv_count = 0
    count_2018 = 0
    count_2019 = 0
    null_arxiv_2018 = 0
    null_arxiv_2019 = 0

    filtered_records = []

    with open(file_path, 'r') as file:
        for line in file:
            record = json.loads(line)
            year = record.get('year')
            arxiv_is_null = record['externalids']['ArXiv'] is None

            if arxiv_is_null:
                null_arxiv_count += 1

            if year == 2018:
                count_2018 += 1
                if arxiv_is_null:
                    null_arxiv_2018 += 1
                else:
                    filtered_records.append(record)
            elif year == 2019:
                count_2019 += 1
                if arxiv_is_null:
                    null_arxiv_2019 += 1
                else:
                    filtered_records.append(record)

    # Écriture des enregistrements filtrés dans un nouveau fichier JSON
    with open(output_file_path, 'w') as output_file:
        for record in filtered_records:
            output_file.write(json.dumps(record) + '\n')

    return {
        "total_null_arxiv": null_arxiv_count,
        "total_2018": count_2018,
        "total_2019": count_2019,
        "null_arxiv_2018": null_arxiv_2018,
        "null_arxiv_2019": null_arxiv_2019,
    }


# Remplacez 'votre_fichier.json' par le chemin vers votre fichier JSON
file_path = 'database_ICML_2018-2022.json'
# Remplacez 'output_file.json' par le chemin où vous souhaitez enregistrer le nouveau fichier JSON
output_file_path = 'database_ICML_2018_2019.json'

results = count_arxiv_and_years(file_path, output_file_path)

print(f"Nombre de lignes avec 'ArXiv' null: {results['total_null_arxiv']}")
print(f"Nombre de lignes datant de 2018: {results['total_2018']}")
print(f"Nombre de lignes datant de 2019: {results['total_2019']}")
print(f"Nombre de lignes de 2018 avec 'ArXiv' null: {results['null_arxiv_2018']}")
print(f"Nombre de lignes de 2019 avec 'ArXiv' null: {results['null_arxiv_2019']}")
