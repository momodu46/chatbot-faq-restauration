import nbformat

cells = []

cells.append(nbformat.v4.new_markdown_cell(
    "# Analyse Exploratoire — Dataset FAQ Restauration Rapide\n\n"
    "Ce notebook analyse le dataset de questions/réponses utilisé par le chatbot FAQ.\n"
    "Il couvre la distribution des catégories, la longueur des questions et réponses,\n"
    "et la couverture thématique du dataset."
))

cells.append(nbformat.v4.new_code_cell(
    "import pandas as pd\n"
    "import matplotlib.pyplot as plt\n"
    "import matplotlib\n\n"
    "matplotlib.rcParams['font.family'] = 'DejaVu Sans'\n"
    "plt.style.use('seaborn-v0_8-whitegrid')\n\n"
    "df = pd.read_csv('../data/faq_dataset.csv')\n"
    "print(f'Dataset chargé : {len(df)} questions, {df[\"categorie\"].nunique()} catégories')\n"
    "df.head()"
))

cells.append(nbformat.v4.new_markdown_cell("## 1. Aperçu général du dataset"))

cells.append(nbformat.v4.new_code_cell(
    "print('=== Informations générales ===')\n"
    "print(f'Nombre total de questions : {len(df)}')\n"
    "print(f'Nombre de catégories : {df[\"categorie\"].nunique()}')\n"
    "print(f'Catégories : {list(df[\"categorie\"].unique())}')\n"
    "print()\n"
    "print('=== Valeurs manquantes ===')\n"
    "print(df.isnull().sum())\n"
    "print()\n"
    "print('=== Types de données ===')\n"
    "print(df.dtypes)"
))

cells.append(nbformat.v4.new_markdown_cell("## 2. Distribution par catégorie"))

cells.append(nbformat.v4.new_code_cell(
    "cat_counts = df['categorie'].value_counts()\n\n"
    "fig, axes = plt.subplots(1, 2, figsize=(14, 5))\n\n"
    "axes[0].bar(cat_counts.index, cat_counts.values, color='steelblue', edgecolor='white')\n"
    "axes[0].set_title('Nombre de questions par catégorie', fontsize=13, fontweight='bold')\n"
    "axes[0].set_xlabel('Catégorie')\n"
    "axes[0].set_ylabel('Nombre de questions')\n"
    "axes[0].tick_params(axis='x', rotation=45)\n\n"
    "axes[1].pie(cat_counts.values, labels=cat_counts.index, autopct='%1.1f%%',\n"
    "            colors=plt.cm.Set3.colors[:len(cat_counts)])\n"
    "axes[1].set_title('Répartition en pourcentage', fontsize=13, fontweight='bold')\n\n"
    "plt.tight_layout()\n"
    "plt.savefig('../data/distribution_categories.png', dpi=150, bbox_inches='tight')\n"
    "plt.show()\n"
    "print(cat_counts)"
))

cells.append(nbformat.v4.new_markdown_cell("## 3. Longueur des questions et réponses"))

cells.append(nbformat.v4.new_code_cell(
    "df['longueur_question'] = df['question'].apply(len)\n"
    "df['longueur_reponse'] = df['reponse'].apply(len)\n"
    "df['nb_mots_question'] = df['question'].apply(lambda x: len(x.split()))\n"
    "df['nb_mots_reponse'] = df['reponse'].apply(lambda x: len(x.split()))\n\n"
    "print('=== Statistiques sur les questions ===')\n"
    "print(df[['longueur_question', 'nb_mots_question']].describe().round(1))\n"
    "print()\n"
    "print('=== Statistiques sur les réponses ===')\n"
    "print(df[['longueur_reponse', 'nb_mots_reponse']].describe().round(1))"
))

cells.append(nbformat.v4.new_code_cell(
    "fig, axes = plt.subplots(1, 2, figsize=(14, 5))\n\n"
    "axes[0].hist(df['nb_mots_question'], bins=10, color='steelblue', edgecolor='white')\n"
    "axes[0].set_title('Distribution du nombre de mots par question', fontsize=13, fontweight='bold')\n"
    "axes[0].set_xlabel('Nombre de mots')\n"
    "axes[0].set_ylabel('Fréquence')\n"
    "axes[0].axvline(df['nb_mots_question'].mean(), color='red', linestyle='--',\n"
    "                label=f'Moyenne : {df[\"nb_mots_question\"].mean():.1f}')\n"
    "axes[0].legend()\n\n"
    "axes[1].hist(df['nb_mots_reponse'], bins=10, color='coral', edgecolor='white')\n"
    "axes[1].set_title('Distribution du nombre de mots par réponse', fontsize=13, fontweight='bold')\n"
    "axes[1].set_xlabel('Nombre de mots')\n"
    "axes[1].set_ylabel('Fréquence')\n"
    "axes[1].axvline(df['nb_mots_reponse'].mean(), color='navy', linestyle='--',\n"
    "                label=f'Moyenne : {df[\"nb_mots_reponse\"].mean():.1f}')\n"
    "axes[1].legend()\n\n"
    "plt.tight_layout()\n"
    "plt.savefig('../data/distribution_longueurs.png', dpi=150, bbox_inches='tight')\n"
    "plt.show()"
))

cells.append(nbformat.v4.new_markdown_cell("## 4. Longueur moyenne des réponses par catégorie"))

cells.append(nbformat.v4.new_code_cell(
    "moy_cat = df.groupby('categorie')['nb_mots_reponse'].mean().sort_values(ascending=False)\n\n"
    "fig, ax = plt.subplots(figsize=(10, 5))\n"
    "ax.barh(moy_cat.index, moy_cat.values, color='mediumseagreen', edgecolor='white')\n"
    "ax.set_title('Longueur moyenne des réponses par catégorie', fontsize=13, fontweight='bold')\n"
    "ax.set_xlabel('Nombre de mots moyen')\n"
    "for i, v in enumerate(moy_cat.values):\n"
    "    ax.text(v + 0.2, i, f'{v:.1f}', va='center')\n\n"
    "plt.tight_layout()\n"
    "plt.savefig('../data/longueur_par_categorie.png', dpi=150, bbox_inches='tight')\n"
    "plt.show()"
))

cells.append(nbformat.v4.new_markdown_cell("## 5. Synthèse"))

cells.append(nbformat.v4.new_code_cell(
    "print('=== SYNTHÈSE DU DATASET ===')\n"
    "print(f'Total questions        : {len(df)}')\n"
    "print(f'Catégories             : {df[\"categorie\"].nunique()}')\n"
    "print(f'Catégorie dominante    : {cat_counts.idxmax()} ({cat_counts.max()} questions)')\n"
    "print(f'Catégorie minoritaire  : {cat_counts.idxmin()} ({cat_counts.min()} questions)')\n"
    "print(f'Longueur moy. question : {df[\"nb_mots_question\"].mean():.1f} mots')\n"
    "print(f'Longueur moy. réponse  : {df[\"nb_mots_reponse\"].mean():.1f} mots')\n"
    "print(f'Valeurs manquantes     : {df.isnull().sum().sum()}')"
))

nb = nbformat.v4.new_notebook()
nb.cells = cells

with open('notebooks/exploration.ipynb', 'w', encoding='utf-8') as f:
    nbformat.write(nb, f)

print('Notebook créé avec succès !')