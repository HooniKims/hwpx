// ==== find ====
                                    let nested_y = if has_preceding_text {
                                        para_y
                                    } else {
                                        inner_area.y
                                    };
                                    let available_h =
                                        (inner_area.height - (nested_y - inner_area.y)).max(0.0);
                                    // TAC(글자처럼 취급) 표: 앞 텍스트 너비만큼 x 오프셋 적용.
// ==== replace ====
                                    let nested_y = if has_preceding_text {
                                        para_y
                                    } else {
                                        inner_area.y
                                    };
                                    // [claude-hwpx cell-tac-table-line] 글이 있는 문단의 글자처럼 취급 표는 글 줄을 다 그린 뒤가 아니라
                                    // 표가 든 줄에 놓는다(위 줄 높이에 표가 이미 들어 있어 표가 제 줄 아래로 한 번 더 내려갔다 — 칸 안
                                    // 그림 표 앞에 글자 하나를 치면 표 높이만큼 빈 자리가 생겼다, 2026-10-11). 쪽 나눔 없는 칸 경로
                                    // (table_layout.rs)와 같이 표 띠 높이와 맞는 줄, 없으면 마지막 줄의 vpos 에 바깥 위 여백을 더한다.
                                    let claude_text_with_tac = nested_table.common.treat_as_char
                                        // 표가 이 쪽에서 시작하는 조각일 때만(이어지는 조각은 쪽 나눔 정보가 위치를 정한다)
                                        && mixed_nested_split.as_ref().map_or(true, |s| {
                                            s.start_row == 0 && s.offset_within_start <= 0.5 && s.content_offset <= 0.5
                                        })
                                        && nested_table.common.height < 0x8000_0000
                                        && !para.line_segs.is_empty()
                                        && composed.lines.iter().any(|line| {
                                            line.runs.iter().any(|run| !run.text.trim().is_empty())
                                        });
                                    let nested_y = if claude_text_with_tac {
                                        let band = i64::from(nested_table.common.height)
                                            + i64::from(nested_table.outer_margin_top)
                                            + i64::from(nested_table.outer_margin_bottom);
                                        let fits = |s: &&crate::model::paragraph::LineSeg| {
                                            (i64::from(s.line_height) - band).abs() <= 10
                                        };
                                        let seg = if para.line_segs.iter().filter(fits).count() == 1 {
                                            para.line_segs.iter().find(fits)
                                        } else {
                                            para.line_segs.last()
                                        };
                                        let first_vpos = para.line_segs[0].vertical_pos;
                                        let seg_vpos = seg.map(|s| s.vertical_pos).unwrap_or(first_vpos);
                                        let om_top = if seg.is_some_and(|s| i64::from(s.line_height) >= band - 10) {
                                            hwpunit_to_px(nested_table.outer_margin_top as i32, self.dpi)
                                        } else {
                                            0.0
                                        };
                                        para_y_before_compose
                                            + hwpunit_to_px(seg_vpos - first_vpos, self.dpi)
                                            + om_top
                                    } else {
                                        nested_y
                                    };
                                    let claude_text_bottom = para_y;
                                    let available_h =
                                        (inner_area.height - (nested_y - inner_area.y)).max(0.0);
                                    // TAC(글자처럼 취급) 표: 앞 텍스트 너비만큼 x 오프셋 적용.
// ==== next ====
                                    para_y = nested_y + visible_table_h;
                                    has_preceding_text = true;
// ==== replace ====
                                    para_y = nested_y + visible_table_h;
                                    if claude_text_with_tac {
                                        // 표가 든 줄은 글 줄을 그릴 때 이미 지나갔다 — 그 아래로 당겨 올리지 않는다
                                        para_y = para_y.max(claude_text_bottom);
                                    }
                                    has_preceding_text = true;
