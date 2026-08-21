# UAV 레이저 배치 및 최적 실내실험 재현 패키지

이 패키지는 다음 두 결과만 재현하도록 최소화했습니다.

1. true-`Snet` 레이저 배치 최적화
2. **최적 배치만** 대상으로 한 실내 파이프라인
   (독립 calibration 11장 + experiment 44장)

평행/최악 배치, 5-fold 교차검증, 실험영상의 체커보드 정답 비교,
Frobenius 지표, 스티칭, 균열분할, 속도측정 및 논문용 보조 그래프는
제거했습니다. 다만 공개된 실내 결과를 바로 확인할 수 있도록 최소 결과
그림 1개는 남겼습니다.

## 실행 환경

기준값과 개발 환경은 MATLAB R2025b 64-bit입니다. 공개 진입점은 MATLAB
코드 분석기를 통과했고, 포함된 UAV 프리셋·카메라 파일·기준 이미지도
R2025b에서 검증했습니다. 배치 기준값은 앞서 완료한 production 실행에서
가져왔습니다. 자세한 상태는 `RELEASE_STATUS.txt`에 기록했습니다.

- MATLAB
- Computer Vision Toolbox
- Image Processing Toolbox
- Optimization Toolbox (배치 최적화에만 필요)

MATLAB에서 이 폴더를 현재 폴더로 설정한 뒤 실행합니다.

```matlab
indoor = run_indoor_only;       % 실내 최적 배치만
placement = run_placement_only; % 저장 프리셋 또는 새 Omega 선택
allResults = run_all;           % placement 선택 후 실내 실행
reference = run_placement_reference; % 저장된 31점 프리셋 재현
```

`run_placement_only`와 `run_all`은 프리셋 사용과 새 영역 지정 중 하나를
선택하게 합니다. 새 영역을 직접 지정할 때만 MATLAB 데스크톱이 필요합니다.
실내 결과는 `outputs/indoor_optimal`, 일반 placement는 `outputs/placement`,
프리셋 기준 실행은 `outputs/placement_reference`에 저장됩니다. 대화상자를
생략하려면 `run_placement_only("preset")` 또는
`run_placement_only("interactive")`를 사용합니다.

## 데이터 독립성

- calibration 11장 원본 index:
  `3, 4, 5, 7, 8, 9, 14, 18, 44, 50, 55`
- experiment 44장: 원본 index `1–44`
- 전 영상 5280×2970
- calibration/experiment SHA-256 중복 0개

카메라 파라미터, 렌즈왜곡 및 두 레이저 계수는 calibration 11장으로만
구합니다. 공개 코드에서는 experiment 44장의 체커보드를 전혀 검출하지
않습니다. 실험영상에는 아래 경로만 적용됩니다.

```text
원영상 -> 빨강/초록 레이저 도심 -> 도심 왜곡보정
       -> 폐쇄형 자세복원 -> homography -> 정사보정
```

저장된 `R_cut`, `G_cut` 또는 기존 도심 MAT 파일도 사용하지 않습니다.

## Placement 자료의 역할

`placement_optimization/data/campram3.mat`은 FOV 및 `Snet` 계산에 쓰는 UAV
카메라 모델입니다. `placement_optimization/data/m3.jpg`는 기체의 장착
가능영역 `Omega`를 정한 별도의 평면 참조사진이고,
`placement_optimization/data/preset_uav_area.mat`에는 저장된 31점 폴리곤과
선택 메타데이터만 들어 있습니다.

`run_placement_only`와 `run_all`은 저장 프리셋과 새 영역 지정 중 하나를
선택하게 합니다. 새 영역 지정에서는 `m3.jpg`에서 (1) 장착 가능영역
`Omega` 다각형을 그리고, (2) 카메라 광축 중심의 투영점을 클릭하고,
(3) 카메라 +z 방향의 점을 클릭합니다. 다각형의 마지막 점은 더블클릭하여
완료합니다. 클릭 없이 기존 수치를 재현하려면 `run_placement_reference`를
사용합니다. 이 함수는 저장된 31점 좌표를 사용하고 별도 폴더에 결과와
기준값 비교표를 저장합니다.

허용 자세영역은 거리마다 각도 범위가 달라지는 JHLEE `PI_dtheta`입니다.
목적함수는 이 종속영역에서 계산한
`Snet = integral_PI_dtheta |det(J)| dtheta dd`이며, 독립적인 상수 theta
범위를 사용하지 않습니다. `m3.jpg`가 별도 참조사진이라는 점을 고려하면,
해당 좌표를 `campram3.mat`으로 왜곡보정하고 mm로 변환하는 결합은 명시된
방법론적 한계로 보아야 합니다.

## 출력

실내 코드는 다음 결과만 만듭니다.

- 카메라 파라미터 CSV/MAT
- 빨강/초록 레이저 계수 CSV
- calibration 도심·체커보드 자세·레이저선 점 QC
- experiment 도심·레이저 자세·3×3 homography CSV
- 레이저 자세 기반 정사영상 44장
- calibration 점과 레이저선, 44장 도심 x, axial distance, surface angle을
  모두 표시한 `optimal_indoor_results_plot.png` 및 vector PDF
- 결과 MAT, 기준값 비교표, 실행 요약

이 결과 그림은 레이저 기반 출력만 보여 주며, experiment 44장의 체커보드
정답이나 오차 지표는 사용하지 않습니다.

정확한 R2025b 기준값은 `metadata/EXPECTED_RESULTS.csv`와 영문 README에
기록했습니다.

## 무결성 및 공개 전 주의

공개용 JPEG은 재압축하지 않고 APP/COM 메타데이터(EXIF/XMP 텔레메트리
포함)를 제거했습니다.
파이프라인이 읽지 않는 보조 JPEG trailer도 제거했으며, 주 영상의 decoded
RGB 픽셀은 원본과 같습니다.
`metadata/DATA_MANIFEST.csv`에 원본/공개본 SHA-256과 decoded-RGB SHA-256을
함께 기록하므로 픽셀 동일성을 확인할 수 있습니다. 전체 패키지는 다음으로
검증합니다.

```bash
python verify_release.py
```

MATLAB 및 Python 소스 파일은 MIT License로 공개합니다(`LICENSE`). 이미지,
표 형식 데이터, 참조 출력, 그림 및 문서는 CC BY 4.0으로 공개합니다
(`DATA_LICENSE.md`). MATLAB과 MathWorks 툴박스는 이 패키지에 포함되지 않습니다.
