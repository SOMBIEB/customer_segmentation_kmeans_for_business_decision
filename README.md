# Customer Segmentation using Machine Learning

## Objective
L’objectif de ce projet est de mieux comprendre une base clients à partir de leurs comportements d’achat, afin d’identifier des profils clairs et exploitables par les équipes métiers.
Plutôt que de regarder les clients individuellement, l’idée est de les regrouper en segments cohérents pour faciliter la prise de décision marketing et commerciale.

---

## Visualisation rapide de quelques resultats 

![Scatter plot showing customer segmentation results using PCA. The plot has five distinct clusters represented by different colors: red, orange, blue, green, and purple. Each cluster corresponds to a customer segment derived from their purchasing behavior. The x-axis is labeled PCA1, and the y-axis is labeled PCA2. The title reads PCA of Customer Segments, and a legend on the right indicates the cluster numbers from 0 to 4 with matching colors.]
---
## Dataset
Le jeu de données regroupe des informations issues de l’historique client et de leurs habitudes d’achat, notamment :

- Le niveau de revenu
- Les dépenses réalisées sur différentes catégories de produits
- La récence du dernier achat
- La fréquence d’achat
- Les canaux utilisés (web et magasin)
etc...
Ces données permettent d’avoir une vision globale du comportement client.

---

## Approach
Le projet a été mené de la même manière qu’en contexte professionnel, étape par étape.

Tout d’abord, les données ont été nettoyées et préparées afin d’éliminer les incohérences et de créer des variables plus parlantes d’un point de vue métier, comme les dépenses totales ou l’ancienneté client.

Ensuite, les variables ont été mises à l’échelle pour garantir un traitement équitable lors de l’entraînement du modèle.

La segmentation a été réalisée à l’aide d’un algorithme de clustering non supervisé, **K-Means**.

Le nombre de segments a été déterminé en combinant plusieurs indicateurs (**Elbow Method**, **Silhouette Score** et **Calinski-Harabasz**), afin de trouver un bon équilibre entre performance statistique et interprétabilité métier.

Enfin, chaque segment a été analysé et interprété afin d’en extraire des profils clients compréhensibles et actionnables.

---

## Results
L’analyse a permis d’identifier **5 segments clients distincts**.

Chaque segment présente des comportements clairement différenciés en termes de revenus, de dépenses, de fréquence d’achat et de canaux utilisés.

Parmi ces profils, on retrouve notamment :
- des clients occasionnels à faible engagement,
- des clients fidèles utilisant plusieurs canaux,
- des clients premium à forte valeur,
- des clients présentant un potentiel d’augmentation de la valeur.

Ces segments permettent de mieux comprendre la structure de la base clients.

---

## Business Value
Cette segmentation apporte une valeur concrète pour l’entreprise :

- meilleure compréhension des différents profils clients,
- optimisation des actions marketing,
- amélioration des stratégies de fidélisation,
- priorisation des efforts commerciaux,
- base solide pour la personnalisation des offres et l’utilisation dans un CRM.

---

## Tech Stack
- Python  
- Pandas / NumPy  
- Scikit-learn  
- Seaborn / Matplotlib  

---

## Next Steps


