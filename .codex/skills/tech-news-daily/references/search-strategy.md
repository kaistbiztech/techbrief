# 후보 풀 수집 전략 (F2)

SKILL.md `[3] 후보 풀 수집` 단계. **매체 직접 접근**을 1차로 두고 쿼리 검색은 보강용으로 쓴다. 목표는 약 **50개 후보**를 평가에 올리는 것.

## 0. 왜 직접 접근인가

키워드 쿼리는 알고리즘 노출에 의존해서 결과가 단조롭고 천천히 갱신된다. 매체 홈·카테고리 페이지를 **직접 fetch**하면 그 매체가 그날 골라 올린 최신 헤드라인을 그대로 받아볼 수 있어 다양성·신선도 둘 다 좋다.

## 1. 1차: 매체 직접 확인

각 매체의 최신 페이지를 Codex의 웹 검색/열기 도구로 확인해 후보를 추출한다. 한 번에 한 매체씩, 그 페이지의 최근 헤드라인 5~10개를 메모.

### 한국 매체 (직접 접근 추천 페이지)

**종합·비즈니스 IT 데일리**
- 한국경제 IT: `https://www.hankyung.com/it`
- 매일경제 IT: `https://www.mk.co.kr/news/it/`
- 조선비즈 테크: `https://biz.chosun.com/it-science/`
- 머니투데이 IT: `https://news.mt.co.kr/v2/section/sectionList.html?code=00`
- ZDNet Korea: `https://zdnet.co.kr/news/?lstcode=0040`
- IT조선: `https://it.chosun.com/`
- 디지털타임스: `https://www.dt.co.kr/`
- 전자신문: `https://www.etnews.com/`
- 디지털데일리: `https://www.ddaily.co.kr/`
- 테크M: `https://www.techm.kr/`
- 블로터(Bloter): `https://www.bloter.net/`
- AI타임스: `https://www.aitimes.com/`
- 헬로티: `https://www.hellot.net/`

**스타트업·벤처**
- 더벤처스퀘어: `https://www.theventures.co/news`
- 플래텀: `https://platum.kr/`
- 와우테일: `https://wowtale.net/`
- 벤처스퀘어: `https://www.venturesquare.net/`
- 비석세스: `https://besuccess.com/`
- 스타트업레시피: `https://startuprecipe.co.kr/`
- 핀테크투데이: `http://www.fintechtoday.co.kr/`

**아티클·인사이트 (C 카테고리 — 매호 1개 필수)**
- 아웃스탠딩: `https://outstanding.kr/`
- 모비인사이드: `https://www.mobiinside.co.kr/`
- 디지털인사이트: `https://ditoday.com/`
- 더스쿠프: `https://www.thescoop.co.kr/`
- EO: `https://eopla.net/`
- 바이라인 네트워크: `https://byline.network/`
- 더기어: `https://thegear.net/`
- 비즈한국: `https://www.bizhankook.com/`
- 인공지능신문: `https://www.aitimes.kr/`
- 한겨레 사이언스온: `https://scienceon.hani.co.kr/`
- 캐리어스(careers): `https://careers.kr/`
- 카카오 테크 블로그: `https://tech.kakao.com/`
- 네이버 D2: `https://d2.naver.com/`
- 우아한형제들 기술블로그: `https://techblog.woowahan.com/`
- 토스 기술블로그: `https://toss.tech/`
- 당근 팀 블로그: `https://medium.com/daangn`

**어그리게이터 (한 번에 다 훑기)**
- Surfit 매거진: `https://mag.surfit.io/`
- Surfit 태그별: `https://www.surfit.io/tag/AI`, `/tag/스타트업`, `/tag/디자인` 등

### 글로벌 매체

**일반 비즈니스**
- Financial Times Tech: `https://www.ft.com/technology`
- Bloomberg Tech: `https://www.bloomberg.com/technology`
- WSJ Tech: `https://www.wsj.com/news/technology`
- Reuters Tech: `https://www.reuters.com/technology/`

**테크 전문**
- TechCrunch: `https://techcrunch.com/`
- The Verge: `https://www.theverge.com/`
- Ars Technica: `https://arstechnica.com/`
- The Information (제한적 접근): `https://www.theinformation.com/`
- TechMeme(어그리게이터): `https://www.techmeme.com/`

**아티클·뉴스레터 (C 카테고리 — 매호 1개 필수)**
- Stratechery (Ben Thompson): `https://stratechery.com/`
- Platformer (Casey Newton): `https://www.platformer.news/`
- Lenny's Newsletter: `https://www.lennysnewsletter.com/`
- Where's Your Ed At (Ed Zitron): `https://www.wheresyoured.at/`
- Import AI (Jack Clark): `https://importai.substack.com/`
- The Pragmatic Engineer: `https://newsletter.pragmaticengineer.com/`
- Benedict Evans: `https://www.ben-evans.com/`
- Not Boring (Packy McCormick): `https://www.notboring.co/`
- Every: `https://every.to/`
- The Generalist: `https://www.thegeneralist.com/`
- MIT Technology Review: `https://www.technologyreview.com/`

**아시아**
- Nikkei Asia: `https://asia.nikkei.com/Business/Technology`
- SCMP Tech: `https://www.scmp.com/tech`
- Rest of World: `https://restofworld.org/`

**오픈소스·보안·트렌드**
- Hacker News 프론트: `https://news.ycombinator.com/`
- GitHub Trending: `https://github.com/trending`
- Product Hunt: `https://www.producthunt.com/`
- The Hacker News (보안): `https://thehackernews.com/`

## 2. 2차: 키워드 쿼리 (보강용, 적게)

직접 fetch에서 부족한 영역이 있을 때만. 1차 쿼리:

- 산업 단위: `"한국 IT 산업 동향 [날짜]"`, `"AI 스타트업 [주]"`
- 결합: `"한국 핀테크 투자 [주]"`, `"국내 반도체 신제품 [날짜]"`

**회사명을 박지 마라 (1차 쿼리에선)**. 1차는 광범위 시야. 2차는 1차에서 발견한 사건의 디테일 검증용으로만 회사명 박음.

## 3. 후보 풀 구성 (목표: 약 50개)

각 후보를 다음 메모로 정리:

```
- 사건 한 줄 요약
- 1차 발생일 (YYYY-MM-DD)  ← coverage 안인지 게이트
- 관련 회사·기관
- 핵심 숫자
- 영문 원문 URL
- 한국어 보도 URL (있으면)
- 카테고리 (A/B/C/D) + 산업 분야
```

## 4. C 카테고리(아티클) 보강 — 매호 1개 필수

`curation-rules.md` §2-1-1에 따라 개인 아티클·블로그·뉴스레터 카드 1개는 무조건 필요.

발견 방법:
- **Surfit 매거진** (`mag.surfit.io`) — 매일 큐레이션된 한국어 인사이트 글
- 카카오/네이버/우아한형제들/토스 **기술블로그 최신 글**
- **Stratechery, Platformer, Lenny's, Where's Your Ed At** 등 영문 인디 뉴스레터
- **MIT Tech Review·The Information**의 사인 있는 인사이드 분석 (스트레이트 뉴스 아님)
- **Hacker News 프론트** 상위 토픽 중 에세이·기술 글

⚠️ **출처 표기 주의**: Surfit·TechMeme 같은 어그리게이터는 발견 채널일 뿐. `sources`에는 **원본 매체 글 URL**을 박는다. (Surfit 매거진 글은 예외 — `mag.surfit.io`를 직접 출처로.)

## 5. 접근 불가 소스 한계

- **Threads / X / Instagram / 카카오톡 채널** 본문은 봇 차단으로 접근 불가
- 페이월 매체 (FT, WSJ, The Information)는 헤드라인·리드만 접근 가능
- 1차 SNS 인용이 필수인 사안은 "기사화·블로그화된 2차 소스" 기반으로만 다룬다
