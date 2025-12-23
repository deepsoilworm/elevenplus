# ⚽ DAU Funnel 시뮬레이터

경기 노드별 유저 흐름 및 리스크 관리를 시각화하는 인터랙티브 대시보드입니다.

## 🚀 빠른 시작

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

### 2. 앱 실행

```bash
streamlit run app.py
```

### 3. 배포 (Streamlit Cloud)

1. GitHub에 이 저장소를 push
2. [Streamlit Cloud](https://streamlit.io/cloud) 접속
3. "New app" → 저장소 선택 → `app.py` 선택
4. Deploy!

무료로 URL 하나로 기획안 공유 가능 🎉

## 📊 기능

### 노드별 현황
- 경기전, 전반전, 하프타임, 후반전, 경기직후 5개 노드
- 각 노드별 유저 구성 (이전유지, 신규, 복귀, 부활)
- 성공률/이탈률 게이지 차트

### Funnel Flow
- Sankey 다이어그램으로 유저 흐름 시각화
- 노드별 유입 구성 파이차트

### 리스크 관리
- At Risk DAU → At Risk WAU → Dead Users 파이프라인
- React Pool / Sur Pool 계산
- 워터폴 차트로 손실 추적

### 데이터 다운로드
- CSV 형식으로 데이터 내보내기

## 🎛️ 조절 가능한 변수

| 카테고리 | 변수 |
|---------|------|
| 신규 유저 | 노드별 신규 유입 수 |
| 복귀 비중 | React Pool에서 각 노드로 복귀하는 비율 |
| 부활 비중 | Sur Pool에서 각 노드로 부활하는 비율 |
| 성공률 | 각 노드에서 다음 노드로 이동하는 성공률 |
| 리스크 전환율 | At Risk → 복귀 전환율 |

## 📁 프로젝트 구조

```
eleven+/
├── app.py              # 메인 Streamlit 앱
├── requirements.txt    # Python 의존성
└── README.md          # 이 파일
```

## 🌐 배포 옵션

| 플랫폼 | 비용 | 특징 |
|--------|------|------|
| Streamlit Cloud | 무료 | 가장 쉬움, GitHub 연동 |
| Heroku | 무료/유료 | 커스텀 도메인 |
| Railway | 무료/유료 | 간편한 배포 |
| AWS/GCP | 유료 | 대규모 트래픽 |

---

Made with ❤️ using Streamlit

