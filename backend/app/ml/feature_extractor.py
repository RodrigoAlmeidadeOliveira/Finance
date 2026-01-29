"""
Módulo de extração de features para classificação de transações.
"""
import re
from typing import Dict, List, Tuple
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer


class TransactionFeatureExtractor:
    """
    Extrai features de transações financeiras para classificação ML.

    Features extraídas:
    - TF-IDF da descrição (texto)
    - Valor normalizado
    - Tipo de transação (débito/crédito)
    - Dia do mês
    """

    def __init__(self, max_features: int = 100):
        """
        Inicializa o extrator de features.

        Args:
            max_features: Número máximo de features TF-IDF
        """
        self.max_features = max_features
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=max_features,
            ngram_range=(1, 2),  # Unigrams e bigrams
            min_df=2,  # Mínimo 2 documentos
            lowercase=True,
            strip_accents='unicode'
        )
        self.fitted = False

    def clean_text(self, text: str) -> str:
        """
        Limpa e normaliza texto da descrição.

        Args:
            text: Texto da descrição da transação

        Returns:
            Texto limpo e normalizado
        """
        if not text or pd.isna(text):
            return ""

        # Converter para string e minúscula
        text = str(text).lower()

        # Remover números de documentos/transações
        text = re.sub(r'\d{4,}', '', text)

        # Remover caracteres especiais, manter apenas letras e espaços
        text = re.sub(r'[^a-záàâãéèêíïóôõöúçñ\s]', ' ', text)

        # Remover espaços múltiplos
        text = re.sub(r'\s+', ' ', text)

        return text.strip()

    def extract_numeric_features(self,
                                 values: np.ndarray,
                                 transaction_types: np.ndarray,
                                 dates: np.ndarray) -> np.ndarray:
        """
        Extrai features numéricas das transações.

        Args:
            values: Array com valores das transações
            transaction_types: Array com tipos (0=débito, 1=crédito)
            dates: Array com datas das transações

        Returns:
            Array com features numéricas [valor_normalizado, tipo, dia_mes]
        """
        # Normalizar valores (log scale para lidar com diferentes magnitudes)
        values_abs = np.abs(values)
        values_normalized = np.log1p(values_abs)  # log(1 + x) para evitar log(0)

        # Extrair dia do mês das datas
        if isinstance(dates[0], pd.Timestamp):
            days_of_month = np.array([d.day for d in dates])
        else:
            days_of_month = pd.to_datetime(dates).day.values

        # Normalizar dia do mês (0-1)
        days_normalized = days_of_month / 31.0

        # Combinar features
        numeric_features = np.column_stack([
            values_normalized,
            transaction_types,
            days_normalized
        ])

        return numeric_features

    def fit_transform(self,
                     descriptions: List[str],
                     values: np.ndarray,
                     transaction_types: np.ndarray,
                     dates: np.ndarray) -> np.ndarray:
        """
        Ajusta o vectorizer e transforma os dados de treinamento.

        Args:
            descriptions: Lista de descrições de transações
            values: Array com valores
            transaction_types: Array com tipos
            dates: Array com datas

        Returns:
            Array com todas as features combinadas
        """
        # Limpar descrições
        cleaned_descriptions = [self.clean_text(desc) for desc in descriptions]

        # Ajustar e transformar TF-IDF
        tfidf_features = self.tfidf_vectorizer.fit_transform(cleaned_descriptions).toarray()

        # Extrair features numéricas
        numeric_features = self.extract_numeric_features(values, transaction_types, dates)

        # Combinar todas as features
        all_features = np.hstack([tfidf_features, numeric_features])

        self.fitted = True
        return all_features

    def transform(self,
                 descriptions: List[str],
                 values: np.ndarray,
                 transaction_types: np.ndarray,
                 dates: np.ndarray) -> np.ndarray:
        """
        Transforma novos dados usando o vectorizer já ajustado.

        Args:
            descriptions: Lista de descrições de transações
            values: Array com valores
            transaction_types: Array com tipos
            dates: Array com datas

        Returns:
            Array com todas as features combinadas
        """
        if not self.fitted:
            raise ValueError("O extrator deve ser ajustado antes de transformar novos dados")

        # Limpar descrições
        cleaned_descriptions = [self.clean_text(desc) for desc in descriptions]

        # Transformar TF-IDF
        tfidf_features = self.tfidf_vectorizer.transform(cleaned_descriptions).toarray()

        # Extrair features numéricas
        numeric_features = self.extract_numeric_features(values, transaction_types, dates)

        # Combinar todas as features
        all_features = np.hstack([tfidf_features, numeric_features])

        return all_features

    def get_feature_names(self) -> List[str]:
        """
        Retorna os nomes de todas as features.

        Returns:
            Lista com nomes das features
        """
        if not self.fitted:
            return []

        tfidf_names = self.tfidf_vectorizer.get_feature_names_out().tolist()
        numeric_names = ['valor_log', 'tipo_transacao', 'dia_mes_norm']

        return tfidf_names + numeric_names
