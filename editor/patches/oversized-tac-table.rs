// ==== find ====
        std::cell::RefCell<Vec<crate::renderer::float_placement::FloatCarveEvidence>>,
}
// ==== replace ====
        std::cell::RefCell<Vec<crate::renderer::float_placement::FloatCarveEvidence>>,
    /// [claude-hwpx oversized-tac-table] 현재 구역의 쪽 본문 높이(px) — 구역 진입 시 set. 기본값 무한대.
    body_height_px: std::cell::Cell<f64>,
}
// ==== next ====
            float_carve_evidence: std::cell::RefCell::new(Vec::new()),
        }
    }
// ==== replace ====
            float_carve_evidence: std::cell::RefCell::new(Vec::new()),
            body_height_px: std::cell::Cell::new(f64::INFINITY),
        }
    }
// ==== next ====
        let layout = PageLayoutInfo::from_page_def(page_def, column_def, self.dpi);
        // [#2403] 소스분기 프로파일 — 엔진(Cell)과 state 에 한 번에 배선.
// ==== replace ====
        let layout = PageLayoutInfo::from_page_def(page_def, column_def, self.dpi);
        self.body_height_px.set(layout.body_area.height);
        // [#2403] 소스분기 프로파일 — 엔진(Cell)과 state 에 한 번에 배선.
// ==== next ====
        self.uses_tac_table_flow(table) || self.tac_table_line_index(para, table, fmt) == Some(0)
    }
// ==== replace ====
        self.uses_tac_table_flow(table)
            || self.tac_table_line_index(para, table, fmt) == Some(0)
            || self.oversized_tac_table(table)
    }

    /// [claude-hwpx oversized-tac-table] 쪽 본문보다 큰 글자처럼 취급 표는 flowWithText 와 무관하게 TAC 다.
    /// 한글은 이런 표를 나누지 않고 새 쪽 맨 위에 통째로 둔다(아래 여백으로 넘침).
    /// #3930 의 `treatAsChar && flowWithText` 근거 표(편람 5개)는 모두 쪽 안에 든다.
    /// 블록 표로 보면 쪽이 나뉘고, 한 문단에 여럿이면 정렬 키(table_flow_tiebreak)가
    /// 블록 표를 첫 줄 TAC 표 앞으로 보내 표 순서까지 뒤집혔다(CORE 실적 새틀).
    fn oversized_tac_table(&self, table: &crate::model::table::Table) -> bool {
        table.common.treat_as_char
            && hwpunit_to_px(table.common.height as i32, self.dpi) > self.body_height_px.get()
    }
