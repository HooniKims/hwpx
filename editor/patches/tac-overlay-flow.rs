// ==== find ====
                let table_flow_end = table_visual_end - physical_outer_box_paint_inset_y;
                if is_tac {
                    let marker_x = tbl_inline_x.unwrap_or(col_area.x + effective_margin);
// ==== replace ====
                // [claude-hwpx tac-overlay-flow] 글자처럼 취급 표는 배치 속성(글 뒤로, 글 앞으로)과 상관없이 줄에 놓여 그 높이를
                // 차지한다(한/글은 배치 속성을 무시한다). layout_table 은 글 뒤로/글 앞으로 표면 흐름을 전진시키지 않고, 저장 줄
                // 배치가 있으면 아래 overlay_tac 보정이 그 줄 높이로 전진시킨다. 줄 배치가 없는 문단(스킬 산출물)은 계산한 줄
                // 높이에 표가 들지 않아 다음 문단이 표 위에 겹쳤다(2026-10-14 전보유예 희망서: 교육청 서식 표 둘이
                // treatAsChar="1" + BEHIND_TEXT). 이때만 표 높이만큼 전진시킨다 — 위아래 배치 표와 같은 결과다
                let table_visual_end = if is_tac
                    && matches!(
                        t.common.text_wrap,
                        crate::model::shape::TextWrap::BehindText
                            | crate::model::shape::TextWrap::InFrontOfText
                    )
                    && crate::renderer::para_has_no_stored_line_segs(para)
                    && table_visual_end <= table_y_start + 0.5
                {
                    table_y_start + table_visual_height
                } else {
                    table_visual_end
                };
                let table_flow_end = table_visual_end - physical_outer_box_paint_inset_y;
                if is_tac {
                    let marker_x = tbl_inline_x.unwrap_or(col_area.x + effective_margin);
