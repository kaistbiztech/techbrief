# JSON 스키마 & 매핑 룰

SKILL.md `[8] JSON 파일 작성` 단계의 세부 정의. 이 스키마는 `index.html`의 `getSources()`와 `renderCards()` 함수가 기대하는 형태와 정확히 일치한다.

## 1. 파일 경로

- 위치: `<프로젝트 루트>/data/<id>.json`
- 파일명: `<YYYY-MM-DD>.json` (예: `2026-05-26.json`)
- 인덱스 파일은 사용하지 않는다 (홈페이지가 폴더를 자동 스캔). 추가 작업 없음.

## 2. 최상위 구조

```json
{
  "id": "YYYY-MM-DD",
  "volumeNumber": <int>,
  "publishedAt": "YYYY-MM-DDT06:30:00+09:00",
  "dayOfWeek": "월",
  "coverage": {
    "from": "YYYY-MM-DD",
    "to": "YYYY-MM-DD",
    "label": "5월 25일 (월)"
  },
  "newsItems": [ /* 정확히 10개 */ ]
}
```

| 필드 | 타입 | 규칙 |
|---|---|---|
| `id` | string | 발행 일자. `YYYY-MM-DD` 정확히. 파일명과 동일해야 함 |
| `volumeNumber` | int | 호 번호. `data/`에서 가장 최근 일자 파일의 `volumeNumber + 1`. 파일 없으면 `1` |
| `publishedAt` | ISO string | `<id>T06:30:00+09:00` 고정 (발행 시간 06:30 KST) |
| `dayOfWeek` | string | 한 글자 (`월`~`일`). 사이트 JS가 "요일"을 자동으로 붙임 |
| `coverage` | object (옵셔널) | 이 호가 다룬 기간. `references/time-context.md`의 산출물. 기존 일자 JSON엔 없어도 됨 |
| `coverage.from` | string | 다룬 기간 시작 (`YYYY-MM-DD`) |
| `coverage.to` | string | 다룬 기간 끝 (`YYYY-MM-DD`) |
| `coverage.label` | string | 사이트 표시용 한국어 라벨 (예: `"5월 25일 (월)"`, `"5월 22~25일 (금·토·일·월)"`) |
| `newsItems` | array | 길이 **정확히 10** |

## 3. newsItem 구조

```json
{
  "order": 1,
  "title": "...",
  "summary": "...(정확히 3문장)",
  "eventDate": "YYYY-MM-DD",
  "keywords": ["키워드1", "키워드2", "키워드3"],
  "sources": [
    { "name": "한국경제", "url": "https://www.hankyung.com/article/..." },
    { "name": "Bloomberg", "url": "https://www.bloomberg.com/news/..." }
  ]
}
```

| 필드 | 타입 | 규칙 |
|---|---|---|
| `order` | int | 1~10. 배열 인덱스와 일치 |
| `title` | string | 한글 24~29자. 회사명·핵심 숫자 포함 |
| `summary` | string | 정확히 3문장, 존댓말 산문, 글머리표 금지 |
| `eventDate` | string | **그 사건의 1차 발생일** (`YYYY-MM-DD`). **반드시 `coverage.from` ~ `coverage.to` 범위 안**. 사이트 카드에 표시됨 |
| `keywords` | array | 3~4개 키워드. 회사명·핵심 숫자·기술명 위주 |
| `sources` | array | 최소 1개. 한국어 매체가 있으면 앞쪽에 배치 |

### keywords 작성 가이드

- **개수**: 카드당 3~4개. 너무 적으면 카드 인식 어렵고, 많으면 클라우드가 잡스러워짐.
- **무엇이 키워드인가**:
  - 회사·기관명 (`OpenAI`, `엔비디아`, `과기정통부`, `Salesforce`)
  - 제품·기술명 (`Claude Opus 4.7`, `HBM4`, `에이전트 코워커`)
  - 핵심 숫자 (`125조 가이던스`, `100조`, `1,170조`, `25% 관세`)
  - 핵심 사건 (`IPO`, `밀라노 사무소`, `공급망 공격`)
- **금지**:
  - 일반 명사(`기술`, `시장`, `회사`)는 정보 가치가 낮으므로 제외.
  - 한 단어가 두 카드에 같이 들어가도 OK (자연스러운 강조).

### sources[i] 구조

| 필드 | 타입 | 규칙 |
|---|---|---|
| `name` | string | 매체 정식 명칭 (약어 금지) |
| `url` | string | `https://` 프로토콜의 직접 기사 URL. 트래킹 파라미터 제거 |

## 4. volumeNumber 자동 계산 절차

1. 프로젝트 루트의 `data/*.json`을 파일명 기준으로 정렬한다.
2. 가장 마지막 파일을 골라 `json.load`로 읽고 `volumeNumber` 추출.
3. `+1` 한 값을 새 파일에 사용.
4. `data/`에 파일이 하나도 없으면 `volumeNumber = 1`.

## 5. dayOfWeek 매핑

JavaScript `Date.getDay()` 표 (`references/time-context.md`와 동일):

| getDay() | dayOfWeek 값 |
|---|---|
| 0 | "일" |
| 1 | "월" |
| 2 | "화" |
| 3 | "수" |
| 4 | "목" |
| 5 | "금" |
| 6 | "토" |

## 6. 사용하지 않는 (구) 포맷

홈페이지는 다음 두 포맷 모두 호환한다:

- 신 포맷 (이 스킬이 쓸 형식): `sources: [{name, url}, ...]`
- 구 포맷 (사용 금지): `sourceName: "...", sourceUrl: "..."`

**이 스킬은 신 포맷만 출력한다.** 단일 출처여도 `sources` 배열에 1개 원소로 담는다.

## 7. 인코딩 & 들여쓰기

- UTF-8.
- 2칸 들여쓰기 (기존 `data/2026-05-25.json`과 동일).
- 한글은 이스케이프하지 않는다 (`ensure_ascii=False` 동등).
- 후행 newline 1개.

## 8. 완성 예시 (정상 파일 1건)

`data/2026-05-25.json`을 참고. 첫 두 항목이 다중 출처 예시이며 이 스킬이 따라야 할 정석 포맷.

## 9. 작성 후 검증

파일을 쓰고 나면 다음 두 가지를 즉시 검증한다:

1. **JSON 파싱 검증**: `python -c "import json; json.load(open('<경로>', encoding='utf-8'))"` 무에러.
2. **필수 필드 검증**: 모든 newsItem에 `order/title/summary/sources` 존재, `sources[].name`과 `sources[].url` 존재, `newsItems` 길이 10.

실패하면 git 단계로 넘어가지 말고 즉시 사용자에게 보고한다.
