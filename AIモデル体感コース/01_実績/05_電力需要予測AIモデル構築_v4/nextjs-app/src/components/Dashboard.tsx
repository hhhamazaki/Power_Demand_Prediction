'use client';

import { FC } from 'react';

interface DashboardProps {
  selectedModel: string;
  setSelectedModel: (model: string) => void;
  selectedYears: string[];
  setSelectedYears: (years: string[]) => void;
  availableYears: string[];
  trainMetrics: { rmse: string; r2: string; mae: string; model: string };
  predMetrics: { rmse: string; r2: string; mae: string; model: string };
  loading: { [key: string]: boolean };
  runDataProcessing: () => void;
  runTraining: () => void;
  getLatestData: () => void;
  runPrediction: () => void;
  runOptimizeYears: () => void;
}

const Dashboard: FC<DashboardProps> = ({
  selectedModel,
  setSelectedModel,
  selectedYears,
  setSelectedYears,
  availableYears,
  trainMetrics,
  predMetrics,
  loading,
  runDataProcessing,
  runTraining,
  getLatestData,
  runPrediction,
  runOptimizeYears,
}) => {
  const models = ['Keras', 'LightGBM', 'PyCaret', 'RandomForest'];

  const toggleYear = (year: string) => {
    setSelectedYears(prev =>
      prev.includes(year) ? prev.filter(y => y !== year) : [...prev, year]
    );
  };

  return (
    <div className="container">
      <div className="header">
        <h1 className="title">電力需要AI予測ダッシュボード</h1>
      </div>

      <div className="grid">
        {/* モデル選択 */}
        <div className="card">
          <h3>モデル</h3>
          <div className="controls" style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '8px' }}>
            {models.map(model => (
              <button
                key={model}
                className={`btn primary ${selectedModel === model ? 'active' : ''}`}
                onClick={() => setSelectedModel(model)}
              >
                {model}
              </button>
            ))}
          </div>
        </div>

        {/* 予測 */}
        <div className="card">
          <h3>予測</h3>
          <div style={{ display: 'flex', gap: '8px', marginBottom: '8px' }}>
            <button
              className={`btn ${loading.latest ? 'running' : ''}`}
              onClick={getLatestData}
              disabled={loading.latest}
              style={{
                background: 'linear-gradient(45deg,#ff00ff,#ff88ff)',
                color: '#fff',
                flex: 1,
              }}
            >
              {loading.latest ? '実行中...' : '最新データ取得'}
            </button>
            <button
              className={`btn ${loading.predict ? 'running' : ''}`}
              onClick={runPrediction}
              disabled={loading.predict}
              style={{
                background: 'linear-gradient(45deg,#ff00ff,#ff88ff)',
                color: '#fff',
                flex: 1,
              }}
            >
              {loading.predict ? '実行中...' : '予測'}
            </button>
          </div>
          <div className="stats">
            <div className="stat">
              RMSE<br />
              <span>{predMetrics.rmse}</span>
            </div>
            <div className="stat">
              R2<br />
              <span>{predMetrics.r2}</span>
            </div>
            <div className="stat">
              MAE<br />
              <span>{predMetrics.mae}</span>
            </div>
            <div className="stat">
              モデル<br />
              <span>{predMetrics.model}</span>
            </div>
          </div>
        </div>

        {/* 学習 */}
        <div className="card">
          <h3>学習</h3>
          <div style={{ display: 'flex', gap: '8px', marginBottom: '8px' }}>
            <button
              className={`btn ${loading.data ? 'running' : ''}`}
              onClick={runDataProcessing}
              disabled={loading.data}
              style={{
                background: 'linear-gradient(45deg,#ff00ff,#ff88ff)',
                color: '#fff',
                flex: 1,
              }}
            >
              {loading.data ? '実行中...' : 'データ処理'}
            </button>
            <button
              className={`btn ${loading.train ? 'running' : ''}`}
              onClick={runTraining}
              disabled={loading.train}
              style={{
                background: 'linear-gradient(45deg,#ff00ff,#ff88ff)',
                color: '#fff',
                flex: 1,
              }}
            >
              {loading.train ? '実行中...' : '学習'}
            </button>
          </div>
          <div className="stats">
            <div className="stat">
              RMSE<br />
              <span>{trainMetrics.rmse}</span>
            </div>
            <div className="stat">
              R2<br />
              <span>{trainMetrics.r2}</span>
            </div>
            <div className="stat">
              MAE<br />
              <span>{trainMetrics.mae}</span>
            </div>
            <div className="stat">
              モデル<br />
              <span>{trainMetrics.model}</span>
            </div>
          </div>
        </div>

        {/* 学習年 */}
        <div className="card">
          <h3>学習年</h3>
          <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap', marginBottom: '12px' }}>
            {availableYears.map(year => (
              <button
                key={year}
                className={`btn ${selectedYears.includes(year) ? 'active glow' : 'inverted'}`}
                onClick={() => toggleYear(year)}
              >
                {year}
              </button>
            ))}
          </div>
          <button
            className={`btn ${loading.optimize ? 'running' : ''}`}
            onClick={runOptimizeYears}
            disabled={loading.optimize}
            style={{
              background: 'linear-gradient(45deg,#ff00ff,#ff88ff)',
              color: '#fff',
              width: '100%',
            }}
          >
            {loading.optimize ? '実行中...' : '組み合わせ検証シミュレーション'}
          </button>
        </div>
      </div>

      {/* グラフエリア */}
      <div className="grid" style={{ marginTop: '16px', gridTemplateColumns: '1fr 1fr' }}>
        <div className="card">
          <h3>予測グラフ</h3>
          <div className="chart-area">
            <img
              src={`/api/images/tomorrow/${selectedModel}/${selectedModel}_tomorrow.png?v=${Date.now()}`}
              alt="予測グラフ"
              onError={(e) => {
                (e.target as HTMLImageElement).style.display = 'none';
              }}
            />
          </div>
        </div>
        <div className="card">
          <h3>学習グラフ</h3>
          <div className="chart-area">
            <img
              src={`/api/images/train/${selectedModel}/${selectedModel}_Ypred.png?v=${Date.now()}`}
              alt="学習グラフ"
              onError={(e) => {
                (e.target as HTMLImageElement).style.display = 'none';
              }}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
