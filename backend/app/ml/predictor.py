"""
Módulo para predição de categorias de transações usando modelo treinado.
"""
from typing import Dict, List, Tuple
import numpy as np
import pandas as pd

from .model_trainer import TransactionClassifierTrainer


class TransactionPredictor:
    """
    Realiza predições de categoria para novas transações.
    """

    def __init__(self, model_path: str):
        """
        Inicializa o preditor carregando modelo treinado.

        Args:
            model_path: Caminho do modelo treinado
        """
        self.model_path = model_path
        self.model_data = TransactionClassifierTrainer.load_model(model_path)
        self.classifier = self.model_data['classifier']
        self.feature_extractor = self.model_data['feature_extractor']
        self.reverse_category_mapping = self.model_data['reverse_category_mapping']
        self.category_mapping = self.model_data['category_mapping']

    def predict_single(self,
                      description: str,
                      value: float,
                      transaction_type: str,
                      date) -> Dict:
        """
        Prediz categoria para uma única transação.

        Args:
            description: Descrição da transação
            value: Valor da transação
            transaction_type: Tipo ('debito' ou 'credito')
            date: Data da transação

        Returns:
            Dicionário com predição e confiança
        """
        return self.predict_batch(
            descriptions=[description],
            values=[value],
            transaction_types=[transaction_type],
            dates=[date]
        )[0]

    def predict_batch(self,
                     descriptions: List[str],
                     values: List[float],
                     transaction_types: List[str],
                     dates: List) -> List[Dict]:
        """
        Prediz categorias para múltiplas transações.

        Args:
            descriptions: Lista de descrições
            values: Lista de valores
            transaction_types: Lista de tipos
            dates: Lista de datas

        Returns:
            Lista de dicionários com predições
        """
        # Converter tipo de transação para numérico
        type_mapping = {'debito': 0, 'crédito': 1, 'credito': 1}
        numeric_types = np.array([
            type_mapping.get(str(t).lower(), 0)
            for t in transaction_types
        ])

        # Extrair features
        X = self.feature_extractor.transform(
            descriptions=descriptions,
            values=np.array(values),
            transaction_types=numeric_types,
            dates=np.array(dates)
        )

        # Fazer predições
        predictions = self.classifier.predict(X)
        probabilities = self.classifier.predict_proba(X)

        # Preparar resultados
        results = []
        for i, (pred_idx, probs) in enumerate(zip(predictions, probabilities)):
            category = self.reverse_category_mapping[pred_idx]
            confidence = float(np.max(probs))

            # Determinar nível de confiança
            if confidence >= 0.8:
                confidence_level = 'high'
            elif confidence >= 0.6:
                confidence_level = 'medium'
            else:
                confidence_level = 'low'

            # Top 3 sugestões alternativas
            top_3_idx = np.argsort(probs)[-3:][::-1]
            suggestions = [
                {
                    'category': self.reverse_category_mapping[idx],
                    'probability': float(probs[idx])
                }
                for idx in top_3_idx
            ]

            results.append({
                'category': category,
                'confidence': confidence,
                'confidence_level': confidence_level,
                'suggestions': suggestions
            })

        return results

    def predict_from_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Prediz categorias para transações em um DataFrame.

        Args:
            df: DataFrame com colunas: description, value, type, date

        Returns:
            DataFrame original com colunas adicionais:
            - predicted_category
            - confidence
            - confidence_level
        """
        # Verificar colunas necessárias
        required_columns = ['description', 'value', 'type', 'date']
        missing_columns = set(required_columns) - set(df.columns)
        if missing_columns:
            raise ValueError(f"Colunas faltando no DataFrame: {missing_columns}")

        # Fazer predições
        predictions = self.predict_batch(
            descriptions=df['description'].tolist(),
            values=df['value'].tolist(),
            transaction_types=df['type'].tolist(),
            dates=df['date'].tolist()
        )

        # Adicionar resultados ao DataFrame
        df_result = df.copy()
        df_result['predicted_category'] = [p['category'] for p in predictions]
        df_result['confidence'] = [p['confidence'] for p in predictions]
        df_result['confidence_level'] = [p['confidence_level'] for p in predictions]

        return df_result

    def get_model_info(self) -> Dict:
        """
        Retorna informações sobre o modelo carregado.

        Returns:
            Dicionário com informações do modelo
        """
        return {
            'model_path': self.model_path,
            'n_categories': len(self.category_mapping),
            'categories': list(self.category_mapping.keys()),
            'training_metrics': self.model_data.get('training_metrics', {}),
            'n_features': len(self.feature_extractor.get_feature_names())
        }

    def validate_predictions(self, df: pd.DataFrame) -> Dict:
        """
        Valida predições comparando com categorias reais.

        Args:
            df: DataFrame com colunas: description, value, type, date, category

        Returns:
            Dicionário com métricas de validação
        """
        if 'category' not in df.columns:
            raise ValueError("DataFrame deve conter coluna 'category' para validação")

        # Fazer predições
        df_pred = self.predict_from_dataframe(df)

        # Calcular métricas
        correct = (df_pred['predicted_category'] == df_pred['category']).sum()
        total = len(df_pred)
        accuracy = correct / total if total > 0 else 0

        # Métricas por nível de confiança
        by_confidence = {}
        for level in ['high', 'medium', 'low']:
            mask = df_pred['confidence_level'] == level
            if mask.sum() > 0:
                level_correct = ((df_pred[mask]['predicted_category'] ==
                                df_pred[mask]['category']).sum())
                level_total = mask.sum()
                level_accuracy = level_correct / level_total
                by_confidence[level] = {
                    'count': int(level_total),
                    'correct': int(level_correct),
                    'accuracy': float(level_accuracy)
                }

        # Erros mais comuns
        errors = df_pred[df_pred['predicted_category'] != df_pred['category']]
        common_errors = errors.groupby(['category', 'predicted_category']).size()
        common_errors = common_errors.sort_values(ascending=False).head(10)

        return {
            'total_samples': int(total),
            'correct_predictions': int(correct),
            'accuracy': float(accuracy),
            'by_confidence_level': by_confidence,
            'common_errors': [
                {
                    'actual': actual,
                    'predicted': pred,
                    'count': int(count)
                }
                for (actual, pred), count in common_errors.items()
            ]
        }
