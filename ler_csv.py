import pandas as pd
import numpy as np
from datetime import datetime

def ler_dados_financeiros(arquivo_csv):
    """
    Lê o arquivo CSV de dados financeiros no formato brasileiro

    Parameters:
    -----------
    arquivo_csv : str
        Caminho para o arquivo CSV

    Returns:
    --------
    pd.DataFrame
        DataFrame com os dados financeiros processados
    """

    # Ler o CSV com encoding UTF-8-sig para lidar com BOM
    df = pd.read_csv(
        arquivo_csv,
        encoding='utf-8-sig',
        sep=',',
        dtype=str  # Ler tudo como string primeiro para processar depois
    )

    # Limpar nomes das colunas (remover espaços extras)
    df.columns = df.columns.str.strip()

    # Processar coluna de Valor
    if 'Valor' in df.columns:
        # Remover 'R$' e espaços
        df['Valor'] = df['Valor'].str.replace('R$', '', regex=False)
        df['Valor'] = df['Valor'].str.strip()

        # Remover pontos de milhar e substituir vírgula por ponto
        df['Valor'] = df['Valor'].str.replace('.', '', regex=False)
        df['Valor'] = df['Valor'].str.replace(',', '.', regex=False)

        # Remover aspas se existirem
        df['Valor'] = df['Valor'].str.replace('"', '', regex=False)

        # Converter para float
        df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce')

    # Processar datas
    colunas_data = ['Data do Evento', 'Data de Efetivação']
    for coluna in colunas_data:
        if coluna in df.columns:
            # Converter para datetime considerando formato DD/MM/YYYY
            df[coluna] = pd.to_datetime(
                df[coluna],
                format='%d/%m/%Y',
                errors='coerce'
            )

    # Limpar espaços em branco nas colunas de texto
    colunas_texto = ['Instituição Financeira', 'Cartão de Crédito',
                     'Categoria', 'Sub Categoria', 'Descrição']
    for coluna in colunas_texto:
        if coluna in df.columns:
            df[coluna] = df[coluna].str.strip()
            # Substituir valores vazios por NaN
            df[coluna] = df[coluna].replace('', np.nan)

    return df


def visualizar_dados(df, n_linhas=10):
    """
    Visualiza informações básicas do DataFrame

    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame a ser visualizado
    n_linhas : int
        Número de linhas a exibir
    """
    print("=" * 80)
    print("INFORMAÇÕES DO DATASET")
    print("=" * 80)

    print(f"\n📊 Dimensões: {df.shape[0]} linhas x {df.shape[1]} colunas")

    print("\n📋 Colunas:")
    print(df.columns.tolist())

    print("\n🔍 Tipos de dados:")
    print(df.dtypes)

    print(f"\n📈 Primeiras {n_linhas} linhas:")
    print(df.head(n_linhas))

    print("\n💰 Estatísticas da coluna Valor:")
    print(df['Valor'].describe())

    print("\n📅 Período dos dados:")
    if 'Data de Efetivação' in df.columns:
        print(f"  Data inicial: {df['Data de Efetivação'].min()}")
        print(f"  Data final: {df['Data de Efetivação'].max()}")

    print("\n🏷️ Categorias únicas:")
    if 'Categoria' in df.columns:
        print(f"  Total: {df['Categoria'].nunique()} categorias")
        print(f"  Categorias: {sorted(df['Categoria'].dropna().unique())}")

    print("\n⚠️ Valores ausentes:")
    print(df.isnull().sum())

    print("\n" + "=" * 80)


if __name__ == "__main__":
    # Arquivo de dados
    arquivo = "dados_treino.csv"

    print("📂 Lendo arquivo:", arquivo)

    try:
        # Ler dados
        df = ler_dados_financeiros(arquivo)

        # Visualizar informações
        visualizar_dados(df, n_linhas=10)

        # Salvar versão processada (opcional)
        arquivo_saida = "dados_processados.csv"
        df.to_csv(arquivo_saida, index=False, encoding='utf-8-sig')
        print(f"\n✅ Dados processados salvos em: {arquivo_saida}")

    except FileNotFoundError:
        print(f"\n❌ Erro: Arquivo '{arquivo}' não encontrado!")
        print("Certifique-se de que o arquivo está no mesmo diretório do script.")

    except Exception as e:
        print(f"\n❌ Erro ao processar arquivo: {str(e)}")
        import traceback
        traceback.print_exc()
