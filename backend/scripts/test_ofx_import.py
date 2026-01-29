#!/usr/bin/env python3
"""
Script para testar importação de arquivo OFX real.

Uso:
    python test_ofx_import.py <caminho_arquivo_ofx>
"""
import sys
import os
from pathlib import Path

# Adicionar o diretório pai ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.importers import OFXImporter
from app.ml import TransactionPredictor
import json


def test_ofx_import(ofx_file_path: str):
    """
    Testa importação e classificação de arquivo OFX.

    Args:
        ofx_file_path: Caminho do arquivo OFX
    """
    print("=" * 80)
    print("TESTE DE IMPORTAÇÃO OFX + CLASSIFICAÇÃO ML")
    print("=" * 80)
    print()

    # 1. Validar arquivo OFX
    print("📋 Validando arquivo OFX...")
    validation = OFXImporter.validate_ofx_file(ofx_file_path)

    if not validation['valid']:
        print(f"❌ Arquivo OFX inválido: {validation['error']}")
        return

    print("✅ Arquivo OFX válido!")
    print()

    # 2. Parsear arquivo OFX
    print("📂 Parseando arquivo OFX...")
    try:
        parsed_data = OFXImporter.parse_ofx_file(ofx_file_path)
    except Exception as e:
        print(f"❌ Erro ao parsear: {str(e)}")
        import traceback
        traceback.print_exc()
        return

    # 3. Mostrar resumo
    print("\n" + "=" * 80)
    print("RESUMO DA IMPORTAÇÃO")
    print("=" * 80)

    summary = OFXImporter.get_import_summary(parsed_data)

    print(f"\n🏦 Instituição: {summary['institution']}")
    print(f"💳 Conta: {summary['account_id']}")
    print(f"📅 Período: {summary['period']['start']} a {summary['period']['end']}")
    print(f"💰 Saldo: R$ {summary['balance']['current']:.2f}")
    if summary['balance']['available']:
        print(f"💵 Saldo Disponível: R$ {summary['balance']['available']:.2f}")

    print(f"\n📊 Transações:")
    print(f"   Total: {summary['transactions']['total']}")
    print(f"   Débitos: {summary['transactions']['debits']['count']} (R$ {summary['transactions']['debits']['total']:.2f})")
    print(f"   Créditos: {summary['transactions']['credits']['count']} (R$ {summary['transactions']['credits']['total']:.2f})")

    # 4. Mostrar algumas transações
    print("\n" + "=" * 80)
    print("PRIMEIRAS 10 TRANSAÇÕES")
    print("=" * 80)

    transactions = parsed_data['transactions'][:10]

    for i, trans in enumerate(transactions, 1):
        print(f"\n{i}. {trans['date'].strftime('%d/%m/%Y')} - {trans['description'][:50]}")
        print(f"   Valor: R$ {trans['amount']:,.2f} ({trans['type']})")
        print(f"   FITID: {trans['fitid']}")

    # 5. Testar classificação ML
    print("\n" + "=" * 80)
    print("CLASSIFICAÇÃO ML DAS TRANSAÇÕES")
    print("=" * 80)

    # Verificar se modelo existe
    model_path = Path(__file__).parent.parent / "app" / "ml" / "models" / "category_classifier.pkl"

    if not model_path.exists():
        print("⚠️  Modelo ML não encontrado. Execute o script de treinamento primeiro:")
        print(f"   python scripts/extract_training_data.py")
        return

    print(f"\n🤖 Carregando modelo ML: {model_path}")
    predictor = TransactionPredictor(str(model_path))

    print(f"\n🎯 Classificando {len(parsed_data['transactions'])} transações...")

    # Preparar dados para predição
    descriptions = [t['description'] for t in parsed_data['transactions']]
    values = [t['amount'] for t in parsed_data['transactions']]
    types = [t['type'] for t in parsed_data['transactions']]
    dates = [t['date'] for t in parsed_data['transactions']]

    # Fazer predições
    predictions = predictor.predict_batch(
        descriptions=descriptions,
        values=values,
        transaction_types=types,
        dates=dates
    )

    # Estatísticas de confiança
    high_conf = sum(1 for p in predictions if p['confidence_level'] == 'high')
    medium_conf = sum(1 for p in predictions if p['confidence_level'] == 'medium')
    low_conf = sum(1 for p in predictions if p['confidence_level'] == 'low')

    print(f"\n📈 Distribuição de confiança:")
    print(f"   Alta (>80%): {high_conf} ({high_conf/len(predictions)*100:.1f}%)")
    print(f"   Média (60-80%): {medium_conf} ({medium_conf/len(predictions)*100:.1f}%)")
    print(f"   Baixa (<60%): {low_conf} ({low_conf/len(predictions)*100:.1f}%)")

    # Mostrar exemplos de classificação
    print("\n" + "=" * 80)
    print("EXEMPLOS DE CLASSIFICAÇÃO (Primeiras 10)")
    print("=" * 80)

    for i in range(min(10, len(predictions))):
        trans = parsed_data['transactions'][i]
        pred = predictions[i]

        print(f"\n{i+1}. {trans['date'].strftime('%d/%m/%Y')} - {trans['description'][:45]}")
        print(f"   Valor: R$ {trans['amount']:,.2f}")
        print(f"   ✨ Categoria: {pred['category']} ({pred['confidence']:.1%} confiança)")

        if pred['confidence_level'] == 'low':
            print(f"   ⚠️  Baixa confiança - revisar manualmente")
            print(f"   💡 Sugestões alternativas:")
            for sug in pred['suggestions'][:3]:
                print(f"      - {sug['category']}: {sug['probability']:.1%}")

    # 6. Resumo de categorias previstas
    print("\n" + "=" * 80)
    print("DISTRIBUIÇÃO POR CATEGORIA PREVISTA")
    print("=" * 80)

    category_counts = {}
    for pred in predictions:
        cat = pred['category']
        category_counts[cat] = category_counts.get(cat, 0) + 1

    sorted_cats = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)

    print()
    for cat, count in sorted_cats:
        pct = count / len(predictions) * 100
        print(f"   {cat}: {count} ({pct:.1f}%)")

    print("\n" + "=" * 80)
    print("✅ TESTE CONCLUÍDO COM SUCESSO!")
    print("=" * 80)
    print()


def main():
    """Função principal."""
    if len(sys.argv) < 2:
        # Tentar encontrar arquivo OFX automaticamente
        possible_paths = [
            Path(__file__).parent.parent.parent / "OFX" / "extrato_BB_NOV_25.ofx",
            Path("OFX/extrato_BB_NOV_25.ofx"),
        ]

        ofx_path = None
        for path in possible_paths:
            if path.exists():
                ofx_path = str(path)
                break

        if not ofx_path:
            print("Uso: python test_ofx_import.py <caminho_arquivo_ofx>")
            print("\nOu coloque o arquivo em: OFX/extrato_BB_NOV_25.ofx")
            sys.exit(1)
    else:
        ofx_path = sys.argv[1]

    if not os.path.exists(ofx_path):
        print(f"❌ Arquivo não encontrado: {ofx_path}")
        sys.exit(1)

    test_ofx_import(ofx_path)


if __name__ == "__main__":
    main()
