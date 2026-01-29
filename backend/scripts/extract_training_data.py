#!/usr/bin/env python3
"""
Script para extrair dados de treinamento da planilha Excel e treinar o modelo ML.

Uso:
    python extract_training_data.py
"""
import sys
import os
from pathlib import Path

# Adicionar o diretório pai ao path para importar módulos do app
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import numpy as np
from datetime import datetime

from app.ml import TransactionClassifierTrainer


def find_excel_file() -> str:
    """
    Encontra o arquivo Excel da planilha financeira.

    Returns:
        Caminho do arquivo Excel
    """
    # Caminhos possíveis
    possible_paths = [
        # Relativo ao script
        Path(__file__).parent.parent.parent / "Planilha" / "Meu_Planner_Financeiro_MacOs_V3-2.xlsm",
        # Diretório atual
        Path("Planilha/Meu_Planner_Financeiro_MacOs_V3-2.xlsm"),
        # Um nível acima
        Path("../Planilha/Meu_Planner_Financeiro_MacOs_V3-2.xlsm"),
    ]

    for path in possible_paths:
        if path.exists():
            return str(path)

    raise FileNotFoundError(
        "Arquivo Excel não encontrado. Procurado em:\n" +
        "\n".join(f"  - {p}" for p in possible_paths)
    )


def extract_transactions_from_excel(excel_path: str) -> pd.DataFrame:
    """
    Extrai transações da planilha Excel (aba FLUXODECAIXA).

    Args:
        excel_path: Caminho do arquivo Excel

    Returns:
        DataFrame com transações processadas
    """
    print(f"📂 Lendo arquivo Excel: {excel_path}")
    print(f"   Procurando aba FLUXODECAIXA...")

    # Ler a aba FLUXODECAIXA com header na linha 4
    # A linha 0 contém os nomes reais das colunas
    df = pd.read_excel(excel_path, sheet_name='FLUXODECAIXA', header=4)

    print(f"   Total de linhas na aba: {len(df)}")

    # Extrair os nomes reais das colunas da primeira linha
    column_names = df.iloc[0].values

    # Criar mapeamento de Unnamed para nomes reais
    column_mapping = {}
    for i, (old_name, new_name) in enumerate(zip(df.columns, column_names)):
        if pd.notna(new_name):
            column_mapping[old_name] = new_name

    # Renomear colunas
    df = df.rename(columns=column_mapping)

    # Remover a linha de cabeçalho que agora está como dados
    df = df.iloc[1:].reset_index(drop=True)

    print(f"   Colunas identificadas: {list(column_mapping.values())}")

    # Identificar colunas necessárias
    date_col = 'Data do Evento'
    desc_col = 'Descrição'
    value_col = 'Valor'
    cat_col = 'Categoria'

    # Verificar se as colunas existem
    required_cols = [date_col, desc_col, value_col, cat_col]
    missing_cols = [col for col in required_cols if col not in df.columns]

    if missing_cols:
        raise ValueError(f"Colunas faltando na aba FLUXODECAIXA: {missing_cols}")

    # Filtrar linhas válidas (com categoria não vazia)
    df_valid = df[df[cat_col].notna()].copy()

    print(f"   Linhas com categoria: {len(df_valid)}")

    # Criar DataFrame padronizado
    transactions = pd.DataFrame({
        'date': pd.to_datetime(df_valid[date_col], errors='coerce'),
        'description': df_valid[desc_col].astype(str),
        'value': pd.to_numeric(df_valid[value_col], errors='coerce'),
        'category': df_valid[cat_col].astype(str),
    })

    # Determinar tipo de transação (débito/crédito) baseado no valor
    transactions['type'] = transactions['value'].apply(
        lambda x: 'credito' if x > 0 else 'debito'
    )

    # Remover valores NaN
    transactions = transactions.dropna(subset=['date', 'value'])

    df_all = transactions

    # Limpar categorias
    df_all['category'] = df_all['category'].str.strip()
    df_all['category'] = df_all['category'].replace('', np.nan)
    df_all = df_all.dropna(subset=['category'])

    # Remover categorias inválidas
    invalid_categories = ['nan', 'none', '-', '']
    df_all = df_all[~df_all['category'].str.lower().isin(invalid_categories)]

    print(f"\n📊 Total de transações extraídas: {len(df_all)}")
    print(f"   Período: {df_all['date'].min()} a {df_all['date'].max()}")
    print(f"   Categorias únicas: {df_all['category'].nunique()}")
    print(f"\n   Distribuição por categoria:")

    category_counts = df_all['category'].value_counts()
    for cat, count in category_counts.items():
        print(f"      {cat}: {count} ({count/len(df_all)*100:.1f}%)")

    return df_all


def main():
    """
    Função principal do script.
    """
    print("=" * 80)
    print("TREINAMENTO DO MODELO ML - CLASSIFICADOR DE TRANSAÇÕES")
    print("=" * 80)
    print()

    try:
        # 1. Encontrar arquivo Excel
        excel_path = find_excel_file()

        # 2. Extrair transações
        df_transactions = extract_transactions_from_excel(excel_path)

        # Verificar quantidade mínima de dados
        if len(df_transactions) < 50:
            raise ValueError(
                f"Poucos dados para treinamento: {len(df_transactions)} transações. "
                "Mínimo recomendado: 50"
            )

        # 3. Preparar diretório do modelo
        model_dir = Path(__file__).parent.parent / "app" / "ml" / "models"
        model_dir.mkdir(parents=True, exist_ok=True)
        model_path = model_dir / "category_classifier.pkl"

        print(f"\n💾 Modelo será salvo em: {model_path}")

        # 4. Treinar modelo
        print("\n" + "=" * 80)
        trainer = TransactionClassifierTrainer(max_features=100, random_state=42)

        metrics = trainer.train(df_transactions, test_size=0.2)

        # 5. Salvar modelo
        trainer.save_model(str(model_path))

        # 6. Resumo final
        print("\n" + "=" * 80)
        print("✅ TREINAMENTO CONCLUÍDO COM SUCESSO!")
        print("=" * 80)
        print(f"\n📈 Métricas finais:")
        print(f"   Acurácia: {metrics['accuracy']:.2%}")
        print(f"   F1-Score: {metrics['f1_score']:.2%}")
        print(f"   CV Score: {metrics['cv_mean']:.2%} (+/- {metrics['cv_std']:.2%})")
        print(f"\n📦 Modelo pronto para uso!")
        print(f"   Localização: {model_path}")
        print(f"   Tamanho: {model_path.stat().st_size / 1024:.1f} KB")

        # Verificar qualidade
        if metrics['accuracy'] < 0.70:
            print("\n⚠️  ATENÇÃO: Acurácia abaixo de 70%")
            print("   Considere:")
            print("   - Adicionar mais dados de treinamento")
            print("   - Verificar qualidade das categorizações")
            print("   - Ajustar hiperparâmetros do modelo")
        elif metrics['accuracy'] >= 0.80:
            print("\n🎉 Excelente! Modelo com alta acurácia (>80%)")

        print()

    except FileNotFoundError as e:
        print(f"\n❌ ERRO: {str(e)}")
        print("\nVerifique se a planilha Excel está no local correto.")
        sys.exit(1)

    except Exception as e:
        print(f"\n❌ ERRO durante o treinamento: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
