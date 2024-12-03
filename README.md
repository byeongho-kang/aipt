# Real Estate Investment AI Agent

이 프로젝트는 부동산 투자 강의 내용을 기반으로 한 AI 에이전트입니다.

## 기능
- 부동산 투자 관련 질문에 대한 답변
- 강의 내용 기반 지식 제공
- 맞춤형 부동산 투자 조언

## 설치 방법
1. 저장소 클론
```bash
git clone [repository-url]
```

2. 가상환경 생성 및 활성화
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. 필요한 패키지 설치
```bash
pip install -r requirements.txt
```

4. 환경 변수 설정
`.env` 파일을 생성하고 필요한 API 키를 설정하세요:
```
OPENAI_API_KEY=your-api-key
```

## 실행 방법
```bash
streamlit run app.py
```
