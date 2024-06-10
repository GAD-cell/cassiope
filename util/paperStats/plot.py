import pandas as pd
import matplotlib.pyplot as plt

# Lecture du fichier CSV
file_path = 'STATS_topic.csv'
df = pd.read_csv(file_path)

# Extraction des colonnes 'Name' et 'citationcount'
data = df[['Name', 'citationcount']]

# Tracé du graphique
plt.figure(figsize=(15, 8))  # Augmenter la taille de la figure pour plus d'espace

# Création du graphique en barres
plt.bar(data['Name'], data['citationcount'])

# Inclinaison des noms pour une meilleure lisibilité
plt.xticks(rotation=45, ha='right')

# Ajout des labels et du titre
plt.xlabel('Name')
plt.ylabel('Citation Count')
plt.title('Citation Count by Name')

# Ajustement de l'espacement pour éviter les chevauchements
plt.tight_layout()  # Pour ajuster l'affichage et éviter les chevauchements

# Espacer les abscisses
ax = plt.gca()
for tick in ax.get_xticklabels():
    tick.set_horizontalalignment('right')

# Affichage du graphique
plt.show()
