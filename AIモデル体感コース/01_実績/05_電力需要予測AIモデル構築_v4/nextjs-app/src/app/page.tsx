'use client';

import { useState, useEffect, useCallback } from 'react';
import Dashboard from '@/components/Dashboard';

export default function Home() {
  const [selectedModel, setSelectedModel] = useState('LightGBM');
  const [selectedYears, setSelectedYears] = useState<string[]>([]);
  const [availableYears, setAvailableYears] = useState<string[]>([]);
  const [trainMetrics, setTrainMetrics] = useState({ rmse: '-', r2: '-', mae: '-', model: '-' });
  const [predMetrics, setPredMetrics] = useState({ rmse: '-', r2: '-', mae: '-', model: '-' });
  const [loading, setLoading] = useState<{ [key: string]: boolean }>({});

  // 利用可能な年を取得
  useEffect(() => {
    fetch('/api/available-years')
      .then(res => res.json())
      .then(data => {
        if (data.years && Array.isArray(data.years)) {
          setAvailableYears(data.years);
          // 初期値として全ての年を選択
          setSelectedYears(data.years);
        }
      })
      .catch(err => console.error('利用可能な年の取得エラー:', err));
  }, []);

  // データ処理実行
  const runDataProcessing = useCallback(async () => {
    setLoading(prev => ({ ...prev, data: true }));
    try {
      const response = await fetch('/api/run-data', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ years: selectedYears }),
      });
      const result = await response.json();
      alert(`データ処理終了: ${result.status || result.message}`);
    } catch (error) {
      alert(`エラー: ${error}`);
    } finally {
      setLoading(prev => ({ ...prev, data: false }));
    }
  }, [selectedYears]);

  // 学習実行
  const runTraining = useCallback(async () => {
    setLoading(prev => ({ ...prev, train: true }));
    try {
      const response = await fetch('/api/run-train', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ model: selectedModel, years: selectedYears }),
      });
      const result = await response.json();
      alert(`学習終了: ${result.status || result.message}`);
      
      // 学習完了後にメトリクスを更新
      if (result.stdout) {
        const extractMetric = (text: string, patterns: string[]) => {
          for (const pattern of patterns) {
            const regex = new RegExp(`${pattern}[:\\s]*([\\d.]+)`, 'i');
            const match = text.match(regex);
            if (match) return match[1];
          }
          return null;
        };

        const rmse = extractMetric(result.stdout, ['RMSE', 'Root Mean Squared Error']);
        const r2 = extractMetric(result.stdout, ['R2', 'R2スコア', 'R2 score']);
        const mae = extractMetric(result.stdout, ['MAE', 'Mean Absolute Error']);

        if (rmse || r2 || mae) {
          setTrainMetrics({
            rmse: rmse || '-',
            r2: r2 || '-',
            mae: mae || '-',
            model: selectedModel,
          });
        }
      }
    } catch (error) {
      alert(`エラー: ${error}`);
    } finally {
      setLoading(prev => ({ ...prev, train: false }));
    }
  }, [selectedModel, selectedYears]);

  // 最新データ取得
  const getLatestData = useCallback(async () => {
    setLoading(prev => ({ ...prev, latest: true }));
    try {
      const response = await fetch('/api/run-tomorrow-data', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      });
      const result = await response.json();
      alert(`最新データ取得: ${result.status || result.message}`);
    } catch (error) {
      alert(`エラー: ${error}`);
    } finally {
      setLoading(prev => ({ ...prev, latest: false }));
    }
  }, []);

  // 予測実行
  const runPrediction = useCallback(async () => {
    setLoading(prev => ({ ...prev, predict: true }));
    try {
      const response = await fetch('/api/run-tomorrow', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ model: selectedModel, years: selectedYears }),
      });
      const result = await response.json();
      alert(`予測終了: ${result.status || result.message}`);
      
      // 予測完了後にメトリクスを更新
      if (result.stdout) {
        const extractMetric = (text: string, patterns: string[]) => {
          for (const pattern of patterns) {
            const regex = new RegExp(`${pattern}[:\\s]*([\\d.]+)`, 'i');
            const match = text.match(regex);
            if (match) return match[1];
          }
          return null;
        };

        const rmse = extractMetric(result.stdout, ['RMSE', 'Root Mean Squared Error']);
        const r2 = extractMetric(result.stdout, ['R2', 'R2スコア', 'R2 score']);
        const mae = extractMetric(result.stdout, ['MAE', 'Mean Absolute Error']);

        if (rmse || r2 || mae) {
          setPredMetrics({
            rmse: rmse || '-',
            r2: r2 || '-',
            mae: mae || '-',
            model: selectedModel,
          });
        }
      }
    } catch (error) {
      alert(`エラー: ${error}`);
    } finally {
      setLoading(prev => ({ ...prev, predict: false }));
    }
  }, [selectedModel, selectedYears]);

  // 組み合わせ検証
  const runOptimizeYears = useCallback(async () => {
    setLoading(prev => ({ ...prev, optimize: true }));
    try {
      const response = await fetch('/api/run-optimize-years', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ model: selectedModel }),
      });
      const result = await response.json();
      alert(`組み合わせ検証終了: ${result.status || result.message}`);
    } catch (error) {
      alert(`エラー: ${error}`);
    } finally {
      setLoading(prev => ({ ...prev, optimize: false }));
    }
  }, [selectedModel]);

  return (
    <Dashboard
      selectedModel={selectedModel}
      setSelectedModel={setSelectedModel}
      selectedYears={selectedYears}
      setSelectedYears={setSelectedYears}
      availableYears={availableYears}
      trainMetrics={trainMetrics}
      predMetrics={predMetrics}
      loading={loading}
      runDataProcessing={runDataProcessing}
      runTraining={runTraining}
      getLatestData={getLatestData}
      runPrediction={runPrediction}
      runOptimizeYears={runOptimizeYears}
    />
  );
}
