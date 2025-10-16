"""
PAC 파일 처리 모듈
"""
from pathlib import Path
from core.ff16tools_wrapper import FF16ToolsWrapper
from core.converter import Converter
from core.config_manager import get_config_manager
from utils.logger import get_logger


class PACHandler:
    """PAC 파일 언팩/팩 처리 클래스"""

    def __init__(self):
        """PAC 핸들러 초기화"""
        self.logger = get_logger()
        self.config = get_config_manager()
        self.converter = Converter()

        # FF16Tools 래퍼 초기화
        ff16tools_path = self.config.get_ff16tools_path()
        self.ff16tools = None

        if ff16tools_path:
            try:
                self.ff16tools = FF16ToolsWrapper(ff16tools_path)
            except Exception as e:
                self.logger.error(f"FF16Tools 초기화 실패: {e}")

    def unpack_and_convert(self, pac_file, output_folder, convert_nxd=True,
                          convert_pzd=True, game='fft', callback=None):
        """
        PAC 파일 언팩 및 NXD/PZD 변환

        Args:
            pac_file: PAC 파일 경로
            output_folder: 출력 폴더 경로
            convert_nxd: NXD → JSON 변환 여부
            convert_pzd: PZD → YAML 변환 여부
            game: 게임 종류 (fft 또는 ff16)
            callback: 진행 상황 콜백 함수

        Returns:
            성공 여부
        """
        if not self.ff16tools:
            self.logger.error("FF16Tools가 초기화되지 않음")
            if callback:
                callback("오류: FF16Tools 경로를 설정해주세요")
            return False

        try:
            # 1. PAC 언팩
            if callback:
                callback(f"PAC 파일 언팩 중: {pac_file}")

            self.logger.info(f"PAC 언팩 시작: {pac_file}")

            if not self.ff16tools.unpack_all(pac_file, output_folder, game):
                self.logger.error("PAC 언팩 실패")
                if callback:
                    callback("오류: PAC 언팩 실패")
                return False

            if callback:
                callback("PAC 언팩 완료")

            # 2. NXD → JSON 변환
            if convert_nxd:
                if callback:
                    callback("NXD 파일을 JSON으로 변환 중...")

                nxd_count = self.converter.convert_nxd_to_json(output_folder)

                if callback:
                    callback(f"NXD → JSON 변환 완료: {nxd_count}개 파일")

            # 3. PZD → YAML 변환
            if convert_pzd:
                if callback:
                    callback("PZD 파일을 YAML로 변환 중...")

                pzd_count = self.converter.convert_pzd_to_yaml(output_folder)

                if callback:
                    callback(f"PZD → YAML 변환 완료: {pzd_count}개 파일")

            self.logger.info("언팩 및 변환 완료")
            if callback:
                callback("모든 작업 완료!")

            return True

        except Exception as e:
            self.logger.error(f"언팩 및 변환 실패: {e}")
            if callback:
                callback(f"오류: {e}")
            return False

    def pack(self, input_folder, output_pac, game='fft', callback=None):
        """
        폴더를 PAC 파일로 팩킹

        Args:
            input_folder: 입력 폴더 경로
            output_pac: 출력 PAC 파일 경로
            game: 게임 종류 (fft 또는 ff16)
            callback: 진행 상황 콜백 함수

        Returns:
            성공 여부
        """
        if not self.ff16tools:
            self.logger.error("FF16Tools가 초기화되지 않음")
            if callback:
                callback("오류: FF16Tools 경로를 설정해주세요")
            return False

        try:
            if callback:
                callback(f"PAC 파일 팩킹 중: {output_pac}")

            self.logger.info(f"PAC 팩킹 시작: {input_folder} → {output_pac}")

            if not self.ff16tools.pack(input_folder, output_pac, game):
                self.logger.error("PAC 팩킹 실패")
                if callback:
                    callback("오류: PAC 팩킹 실패")
                return False

            self.logger.info("PAC 팩킹 완료")
            if callback:
                callback("PAC 팩킹 완료!")

            return True

        except Exception as e:
            self.logger.error(f"PAC 팩킹 실패: {e}")
            if callback:
                callback(f"오류: {e}")
            return False

    def apply_translation_and_pack(self, csv_folder, source_folder, output_pac,
                                   delete_yaml_json=False, delete_other=False,
                                   apply_yaml=True, apply_json=True, skip_packing=False,
                                   game='fft', callback=None):
        """
        번역 적용 및 PAC 팩킹

        Args:
            csv_folder: CSV 폴더 경로
            source_folder: 원본 YAML/JSON 폴더 경로
            output_pac: 출력 PAC 파일 경로
            delete_yaml_json: YAML/JSON 삭제 여부
            delete_other: 기타 파일 삭제 여부
            apply_yaml: YAML 파일에 CSV 적용 여부
            apply_json: JSON 파일에 CSV 적용 여부
            skip_packing: 패킹 건너뛰기 여부
            game: 게임 종류
            callback: 진행 상황 콜백 함수

        Returns:
            성공 여부
        """
        try:
            from core.csv_handler import CSVHandler
            csv_handler = CSVHandler()

            # 1. CSV 폴더에서 모든 번역 로드
            if callback:
                callback(f"1/5: 모든 CSV 파일에서 번역 데이터 로딩 중...")
            
            translations = csv_handler.load_all_translations(csv_folder)
            if not translations:
                self.logger.warning("CSV 파일에서 번역 데이터를 찾을 수 없습니다.")
                # 번역 데이터가 없어도 나머지 프로세스는 진행될 수 있으므로 여기서 중단하지 않습니다.
            else:
                if callback:
                    callback(f"번역 데이터 {len(translations)}개 로드 완료.")

            # 2. 로드된 번역을 YAML/JSON 파일에 적용
            if callback:
                callback(f"2/5: CSV 번역을 YAML/JSON 파일에 적용 중...")
            
            updated_files_count = csv_handler.apply_translations_to_folder(source_folder, translations, apply_yaml, apply_json)
            self.logger.info(f"{updated_files_count}개의 파일에 번역이 적용되었습니다.")

            if callback:
                applied_types = []
                if apply_yaml:
                    applied_types.append("YAML")
                if apply_json:
                    applied_types.append("JSON")
                callback(f"CSV 적용 완료 (대상: {', '.join(applied_types)})")

            # 3. YAML → PZD 변환
            if apply_yaml:
                if callback:
                    callback(f"3/5: YAML을 PZD로 변환 중...")

                yaml_count = self.converter.convert_yaml_to_pzd(source_folder)

                if callback:
                    callback(f"YAML → PZD 변환 완료: {yaml_count}개")
            else:
                self.logger.info("YAML -> PZD 변환을 건너뜁니다.")

            # 4. JSON → NXD 변환
            if apply_json:
                if callback:
                    callback(f"4/5: JSON을 NXD로 변환 중...")

                json_count = self.converter.convert_json_to_nxd(source_folder)

                if callback:
                    callback(f"JSON → NXD 변환 완료: {json_count}개")
            else:
                self.logger.info("JSON -> NXD 변환을 건너뜁니다.")

            # 5. 불필요한 파일 삭제
            if delete_yaml_json or delete_other:
                if callback:
                    callback(f"5/5: 불필요한 파일 삭제 중...")

                self._cleanup_files(source_folder, delete_yaml_json, delete_other)

                if callback:
                    callback("파일 정리 완료")
            else:
                self.logger.info("파일 정리를 건너뜁니다.")

            # 6. PAC 팩킹
            if not skip_packing:
                if callback:
                    callback(f"최종 단계: PAC 파일 팩킹 중...")

                if not self.pack(source_folder, output_pac, game, callback):
                    return False

                self.logger.info("번역 적용 및 팩킹 완료")
                if callback:
                    callback("모든 작업 완료!")
            else:
                self.logger.info("번역 적용 완료 (패킹 건너뜀)")
                if callback:
                    callback("번역 적용 완료! (패킹은 건너뛰었습니다)")

            return True

        except Exception as e:
            self.logger.error(f"번역 적용 및 팩킹 실패: {e}")
            if callback:
                callback(f"오류: {e}")
            return False

    def _cleanup_files(self, folder, delete_yaml_json, delete_other):
        """
        불필요한 파일 삭제

        Args:
            folder: 대상 폴더
            delete_yaml_json: YAML/JSON 삭제 여부
            delete_other: 기타 파일 삭제 여부
        """
        folder_path = Path(folder)

        if delete_yaml_json:
            # YAML 파일 삭제
            yaml_files = list(folder_path.rglob('*.yaml'))
            for yaml_file in yaml_files:
                yaml_file.unlink()
                self.logger.info(f"삭제: {yaml_file}")

            # JSON 파일 삭제
            json_files = list(folder_path.rglob('*.json'))
            for json_file in json_files:
                json_file.unlink()
                self.logger.info(f"삭제: {json_file}")

        if delete_other:
            # NXD/PZD 이외의 파일 찾기
            all_files = [f for f in folder_path.rglob('*') if f.is_file()]

            for file in all_files:
                if file.suffix not in ['.nxd', '.pzd']:
                    # 여기서는 자동으로 삭제하지 않고 로그만 남김
                    # 실제 삭제는 사용자 확인 후 진행해야 함
                    self.logger.info(f"삭제 대상: {file}")
