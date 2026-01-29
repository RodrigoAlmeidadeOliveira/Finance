"""
Módulo para treinamento do modelo de classificação de transações.
"""
import os
from typing import Dict, Tuple
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    accuracy_score,
    f1_score
)
import joblib

from .feature_extractor import TransactionFeatureExtractor


class TransactionClassifierTrainer:
    """
    Treina um classificador Random Forest para categorizar transações.
    """

    def __init__(self, max_features: int = 100, random_state: int = 42):
        """
        Inicializa o treinador.

        Args:
            max_features: Número máximo de features TF-IDF
            random_state: Seed para reprodutibilidade
        """
        self.random_state = random_state
        self.feature_extractor = TransactionFeatureExtractor(max_features=max_features)
        self.classifier = RandomForestClassifier(
            n_estimators=200,
            max_depth=20,
            min_samples_split=5,
            min_samples_leaf=2,
            class_weight='balanced',  # Lidar com classes desbalanceadas
            random_state=random_state,
            n_jobs=-1  # Usar todos os cores disponíveis
        )
        self.category_mapping = {}
        self.reverse_category_mapping = {}
        self.training_metrics = {}

    def prepare_data(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepara os dados para treinamento.

        Args:
            df: DataFrame com colunas: description, value, type, date, category

        Returns:
            Tupla (X, y) com features e labels
        """
        # Verificar colunas necessárias
        required_columns = ['description', 'value', 'type', 'date', 'category']
        missing_columns = set(required_columns) - set(df.columns)
        if missing_columns:
            raise ValueError(f"Colunas faltando no DataFrame: {missing_columns}")

        # Remover linhas sem categoria
        df = df.dropna(subset=['category'])

        # Criar mapeamento de categorias para números
        unique_categories = sorted(df['category'].unique())
        self.category_mapping = {cat: idx for idx, cat in enumerate(unique_categories)}
        self.reverse_category_mapping = {idx: cat for cat, idx in self.category_mapping.items()}

        # Converter tipo de transação para numérico (0=débito, 1=crédito)
        type_mapping = {'debito': 0, 'crédito': 1, 'credito': 1}
        transaction_types = df['type'].map(lambda x: type_mapping.get(str(x).lower(), 0)).values

        # Extrair features
        X = self.feature_extractor.fit_transform(
            descriptions=df['description'].tolist(),
            values=df['value'].values,
            transaction_types=transaction_types,
            dates=df['date'].values
        )

        # Converter categorias para labels numéricas
        y = df['category'].map(self.category_mapping).values

        return X, y

    def train(self, df: pd.DataFrame, test_size: float = 0.2) -> Dict:
        """
        Treina o modelo e avalia performance.

        Args:
            df: DataFrame com dados de treinamento
            test_size: Proporção dos dados para teste

        Returns:
            Dicionário com métricas de treinamento
        """
        print(f"📊 Preparando dados de treinamento...")
        print(f"   Total de transações: {len(df)}")

        # Preparar dados
        X, y = self.prepare_data(df)

        print(f"   Features extraídas: {X.shape[1]}")
        print(f"   Categorias únicas: {len(self.category_mapping)}")
        print(f"   Categorias: {list(self.category_mapping.keys())}")

        # Split train/test
        X_train, X_test, y_train, y_test = train_test_split(
            X, y,
            test_size=test_size,
            random_state=self.random_state,
            stratify=y  # Manter proporção de classes
        )

        print(f"\n🎯 Treinando Random Forest...")
        print(f"   Train: {len(X_train)} | Test: {len(X_test)}")

        # Treinar modelo
        self.classifier.fit(X_train, y_train)

        # Avaliar no conjunto de teste
        y_pred = self.classifier.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred, average='weighted')

        print(f"\n✅ Treinamento concluído!")
        print(f"   Acurácia: {accuracy:.2%}")
        print(f"   F1-Score: {f1:.2%}")

        # Cross-validation
        print(f"\n🔄 Executando validação cruzada (5-fold)...")
        cv_scores = cross_val_score(
            self.classifier, X, y,
            cv=5,
            scoring='accuracy',
            n_jobs=-1
        )
        print(f"   CV Acurácia: {cv_scores.mean():.2%} (+/- {cv_scores.std():.2%})")

        # Relatório de classificação
        print(f"\n📋 Relatório por categoria:")
        # Usar labels para garantir que todas as classes sejam incluídas
        all_labels = sorted(self.reverse_category_mapping.keys())
        all_target_names = [self.reverse_category_mapping[i] for i in all_labels]

        report = classification_report(
            y_test, y_pred,
            labels=all_labels,
            target_names=all_target_names,
            output_dict=True,
            zero_division=0
        )

        for category, metrics in report.items():
            if isinstance(metrics, dict) and 'precision' in metrics:
                # Pular categorias com suporte 0 (não aparecem no test set)
                if metrics.get('support', 0) > 0:
                    print(f"   {category}:")
                    print(f"      Precision: {metrics['precision']:.2%}")
                    print(f"      Recall: {metrics['recall']:.2%}")
                    print(f"      F1-Score: {metrics['f1-score']:.2%}")
                    print(f"      Amostras: {int(metrics['support'])}")

        # Feature importance
        feature_names = self.feature_extractor.get_feature_names()
        feature_importance = self.classifier.feature_importances_
        top_features_idx = np.argsort(feature_importance)[-10:][::-1]

        print(f"\n🔝 Top 10 features mais importantes:")
        for idx in top_features_idx:
            print(f"   {feature_names[idx]}: {feature_importance[idx]:.4f}")

        # Salvar métricas
        self.training_metrics = {
            'accuracy': float(accuracy),
            'f1_score': float(f1),
            'cv_mean': float(cv_scores.mean()),
            'cv_std': float(cv_scores.std()),
            'n_samples_train': int(len(X_train)),
            'n_samples_test': int(len(X_test)),
            'n_features': int(X.shape[1]),
            'n_categories': int(len(self.category_mapping)),
            'classification_report': report
        }

        return self.training_metrics

    def save_model(self, model_path: str):
        """
        Salva o modelo treinado em disco.

        Args:
            model_path: Caminho para salvar o modelo
        """
        # Criar diretório se não existir
        os.makedirs(os.path.dirname(model_path), exist_ok=True)

        # Salvar modelo completo
        model_data = {
            'classifier': self.classifier,
            'feature_extractor': self.feature_extractor,
            'category_mapping': self.category_mapping,
            'reverse_category_mapping': self.reverse_category_mapping,
            'training_metrics': self.training_metrics
        }

        joblib.dump(model_data, model_path)
        print(f"\n💾 Modelo salvo em: {model_path}")

    @staticmethod
    def load_model(model_path: str) -> Dict:
        """
        Carrega um modelo treinado do disco.

        Args:
            model_path: Caminho do modelo

        Returns:
            Dicionário com componentes do modelo
        """
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Modelo não encontrado em: {model_path}")

        model_data = joblib.load(model_path)
        print(f"✅ Modelo carregado de: {model_path}")
        print(f"   Categorias: {len(model_data['category_mapping'])}")
        print(f"   Acurácia: {model_data['training_metrics'].get('accuracy', 0):.2%}")

        return model_data
