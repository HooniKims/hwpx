// ==== find ====
  moveHorizontal(delta: number): void {
    this.preferredX = null;
    this.atLineEnd = false;
// ==== replace ====
  moveHorizontal(delta: number): void {
    this.preferredX = null;
    this.atLineEnd = false;

    // [claude-hwpx table-arrow-edge] 표 바로 앞에서 → 는 첫 칸, 바로 뒤에서 ← 는 마지막 칸 끝으로 들어간다(한/글)
    if (!this.anchor && this.claudeEnterAdjacentTable(delta)) return;
// ==== next ====
        this.moveToCellPrev();
// ==== replace ====
        this.moveToCellPrev(true);
// ==== next ====
          this.moveToCellNext();
// ==== replace ====
          this.moveToCellNext(true);
// ==== next ====
  moveToCellNext(): void {
// ==== replace ====
  moveToCellNext(claudeBeside = false): void {
// ==== next ====
  moveToCellPrev(): void {
// ==== replace ====
  moveToCellPrev(claudeBeside = false): void {
// ==== next ====
        this.exitTable(1);
// ==== replace ====
        if (claudeBeside && !this.anchor && this.claudeExitTableBeside(1)) return;
        this.exitTable(1);
// ==== next ====
        this.exitTable(-1);
// ==== replace ====
        if (claudeBeside && !this.anchor && this.claudeExitTableBeside(-1)) return;
        this.exitTable(-1);
// ==== next ====
      // WASM 결과가 hitTest의 cursorRect와 페이지가 다르면 잘못된 좌표 → 폴백
// ==== replace ====
      this.claudeTableSideRect();
      // WASM 결과가 hitTest의 cursorRect와 페이지가 다르면 잘못된 좌표 → 폴백
// ==== next ====
      this.rect = { ...pos.cursorRect };
      this.focusedGeometryValid = true;
// ==== replace ====
      this.rect = { ...pos.cursorRect };
      this.claudeTableSideRect();
      this.focusedGeometryValid = true;
// ==== next ====
  /** 표 밖으로 나가기 (delta: +1=다음 위치, -1=이전 위치) — Tab/Shift+Tab 전용 */
// ==== replace ====
  // ─── [claude-hwpx table-arrow-edge] 표 앞뒤 캐럿(한/글처럼, 2026-10-11 사용자 요청) ───
  // 마지막 칸 끝에서 → 는 표 바로 뒤, 첫 칸 처음에서 ← 는 표 바로 앞으로 나간다(종전에는 다음 문단 처음과
  // 표 문단 0번 자리). 표 앞뒤 캐럿은 표 테두리 바깥에 표 높이로 그린다 — 엔진 좌표는 테두리와 겹친
  // 한 줄 높이라 보이지 않았다. 표 속 표도 같다(칸 경로 + 엔진 convertCaretOffset 모드 7).

  /** 캐럿이 있는 문단: host = 본문 문단 번호, base = 그 문단까지의 칸 경로(본문이면 []) */
  private claudeCaretContainer(): { sec: number; host: number; base: CellPathEntry[] } | null {
    const pos = this.position;
    if (pos.isTextBox) return null;
    if (!this.isInCell()) return { sec: pos.sectionIndex, host: pos.paragraphIndex, base: [] };
    if (pos.parentParaIndex === undefined) return null;
    const base = (pos.cellPath?.length ?? 0) > 0
      ? pos.cellPath!.map((e) => ({ ...e }))
      : [{ controlIndex: pos.controlIndex!, cellIndex: pos.cellIndex!, cellParaIndex: pos.cellParaIndex! }];
    return { sec: pos.sectionIndex, host: pos.parentParaIndex, base };
  }

  /** 캐럿 칸 [off, off+1) 에 있는 표: 컨트롤 번호와 표 경로. 개체 칸이 아니거나 표가 아니면 null */
  private claudeTableAtSlot(c: { sec: number; host: number; base: CellPathEntry[] }, off: number): CellPathEntry[] | null {
    const doc = (this.wasm as any).doc;
    if (off < 0 || typeof doc?.convertCaretOffset !== 'function') return null;
    const basePath = c.base.length ? JSON.stringify(c.base) : '';
    try {
      if (off >= doc.convertCaretOffset(c.sec, c.host, basePath, 0, 5)) return null;
      // 글자 축으로 바꿔 같은 자리면 그 칸은 글자가 아니라 개체다
      if (doc.convertCaretOffset(c.sec, c.host, basePath, off, 0) !== doc.convertCaretOffset(c.sec, c.host, basePath, off + 1, 0)) return null;
    } catch { return null; }
    const count = c.base.length ? 32 : this.wasm.getControlTextPositions(c.sec, c.host).length;
    for (let k = 0; k < count; k++) {
      try {
        if (doc.convertCaretOffset(c.sec, c.host, basePath, k, 7) !== off) continue;
        const path = [...c.base, { controlIndex: k, cellIndex: 0, cellParaIndex: 0 }];
        this.wasm.getTableDimensionsByPath(c.sec, c.host, JSON.stringify(path));
        return path;
      } catch { /* 표가 아니다 */ }
    }
    return null;
  }

  private claudeEnterAdjacentTable(delta: number): boolean {
    const c = this.claudeCaretContainer();
    if (!c) return false;
    const off = this.position.charOffset;
    const table = this.claudeTableAtSlot(c, delta > 0 ? off : off - 1);
    if (!table) return false;
    try {
      const { cellCount } = this.wasm.getTableDimensionsByPath(c.sec, c.host, JSON.stringify(table));
      if (!cellCount) return false;
      const cell = delta > 0 ? 0 : cellCount - 1;
      const at = (p: number) => table.map((e, i) => (i < table.length - 1 ? e : { ...e, cellIndex: cell, cellParaIndex: p }));
      let cpi = 0;
      let coff = 0;
      if (delta < 0) {
        cpi = Math.max(0, this.wasm.getCellParagraphCountByPath(c.sec, c.host, JSON.stringify(at(0))) - 1);
        coff = this.wasm.getCellParagraphLengthByPath(c.sec, c.host, JSON.stringify(at(cpi)));
      }
      const path = at(cpi);
      this.position = {
        sectionIndex: c.sec, paragraphIndex: cpi, charOffset: coff,
        parentParaIndex: c.host, controlIndex: path[0].controlIndex,
        cellIndex: cell, cellParaIndex: cpi, cellPath: path,
      };
      this.updateRect();
      return true;
    } catch {
      return false;
    }
  }

  private claudeExitTableBeside(delta: number): boolean {
    const c = this.claudeCaretContainer();
    if (!c || !c.base.length) return false;
    const table = c.base[c.base.length - 1];
    const outer = c.base.slice(0, -1);
    try {
      const slot = (this.wasm as any).doc.convertCaretOffset(c.sec, c.host, outer.length ? JSON.stringify(outer) : '', table.controlIndex, 7);
      const off = delta > 0 ? slot + 1 : slot;
      if (!outer.length) {
        this.position = { sectionIndex: c.sec, paragraphIndex: c.host, charOffset: off };
      } else {
        const last = outer[outer.length - 1];
        this.position = {
          sectionIndex: c.sec, paragraphIndex: last.cellParaIndex, charOffset: off,
          parentParaIndex: c.host, controlIndex: outer[0].controlIndex,
          cellIndex: last.cellIndex, cellParaIndex: last.cellParaIndex, cellPath: outer,
        };
      }
      this.updateRect();
      return true;
    } catch {
      return false;
    }
  }

  /** 캐럿이 표 바로 앞이나 뒤면 표 테두리 바깥에 표 높이로 그린다 */
  private claudeTableSideRect(): void {
    if (!this.rect) return;
    const c = this.claudeCaretContainer();
    if (!c) return;
    const off = this.position.charOffset;
    let table = this.claudeTableAtSlot(c, off - 1);
    const right = !!table;
    if (!table) table = this.claudeTableAtSlot(c, off);
    if (!table) return;
    try {
      const page = this.rect.pageIndex;
      const boxes = this.wasm.getTableCellBboxesByPath(c.sec, c.host, JSON.stringify(table)).filter((b) => b.pageIndex === page);
      if (!boxes.length) return;
      const x0 = Math.min(...boxes.map((b) => b.x));
      const x1 = Math.max(...boxes.map((b) => b.x + b.w));
      const y0 = Math.min(...boxes.map((b) => b.y));
      const y1 = Math.max(...boxes.map((b) => b.y + b.h));
      this.rect = { ...this.rect, x: right ? x1 + 2 : x0 - 2, y: y0, height: y1 - y0 };
    } catch { /* 엔진 좌표 그대로 */ }
  }

  /** 표 밖으로 나가기 (delta: +1=다음 위치, -1=이전 위치) — Tab/Shift+Tab 전용 */
