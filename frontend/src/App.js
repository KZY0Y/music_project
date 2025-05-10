import React, { useState } from 'react';
import './App.css';

function App() {
  const [image, setImage] = useState(null);
  const [preview, setPreview] = useState(null);
  const [analyzeResult, setAnalyzeResult] = useState(null);
  const [music, setMusic] = useState(null);
  const [spotifyUrl, setSpotifyUrl] = useState(null);
  const [loading, setLoading] = useState(false);

  // 上传图片
  const handleImageChange = (e) => {
    const file = e.target.files[0];
    setImage(file);
    setPreview(URL.createObjectURL(file));
  };

  // 提交图片并获取推荐
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!image) return;
    setLoading(true);
    setAnalyzeResult(null);
    setMusic(null);
    setSpotifyUrl(null);
    // 1. 上传图片
    const formData = new FormData();
    formData.append('file', image);
    const uploadRes = await fetch('http://localhost:8000/upload_image', {
      method: 'POST',
      body: formData,
    });
    const uploadData = await uploadRes.json();
    // 2. 图片分析
    const analyzeRes = await fetch('http://localhost:8000/analyze_image', {
      method: 'POST',
      body: new URLSearchParams({ file_path: uploadData.file_path }),
    });
    const analyzeData = await analyzeRes.json();
    setAnalyzeResult(analyzeData);
    // 3. 推荐音乐
    const musicRes = await fetch('http://localhost:8000/recommend_music', {
      method: 'POST',
      body: new URLSearchParams(analyzeData),
    });
    const musicData = await musicRes.json();
    setMusic(musicData);
    // 4. 获取Spotify播放链接
    const spotifyRes = await fetch('http://localhost:8000/spotify_play', {
      method: 'POST',
      body: new URLSearchParams(musicData),
    });
    const spotifyData = await spotifyRes.json();
    setSpotifyUrl(spotifyData.spotify_url);
    setLoading(false);
  };

  return (
    <div className="app-bg">
      <div className="app-header">
        <span className="app-logo">🎵</span>
        <span className="app-title">看图推荐音乐 byKZY</span>
        <span className="app-logo">🎵</span>
      </div>
      <div className="main-card">
        <form className="upload-form" onSubmit={handleSubmit}>
          <label className="upload-label">
            <input type="file" accept="image/*" onChange={handleImageChange} />
            <span className="upload-btn">{image ? '已选择图片' : '选择图片'}</span>
          </label>
          <button className="analyze-btn" type="submit" disabled={loading}>
            {loading ? '分析中...' : '上传并推荐音乐'}
          </button>
        </form>
        <div className="content-row">
          {preview && (
            <div className="img-preview-card">
              <img src={preview} alt="预览" className="img-preview" />
            </div>
          )}
          <div className="result-card">
            <div className="result-section">
              <h4>图片分析结果</h4>
              <ul>
                <li>内容：{analyzeResult?.content || ''}</li>
                <li>心情：{analyzeResult?.mood || ''}</li>
                <li>季节：{analyzeResult?.season || ''}</li>
                <li>场景：{analyzeResult?.scene || ''}</li>
                <li>时间：{analyzeResult?.time || ''}</li>
              </ul>
            </div>
            <div className="result-section">
              <h4>推荐音乐</h4>
              <div>曲目：{music?.song || ''}</div>
              <div>歌手：{music?.artist || ''}</div>
            </div>
            {spotifyUrl && (
              <div className="player-section">
                <iframe
                  src={spotifyUrl}
                  width="100%"
                  height="80"
                  frameBorder="0"
                  allow="autoplay; clipboard-write; encrypted-media; picture-in-picture"
                  title="Spotify Player"
                  style={{ borderRadius: 8, marginTop: 12 }}
                ></iframe>
              </div>
            )}
          </div>
        </div>
      </div>
      <div className="footer">© 2025 看图推荐音乐 byKZY</div>
    </div>
  );
}

export default App;