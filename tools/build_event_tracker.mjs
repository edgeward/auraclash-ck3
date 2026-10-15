// Build with the external bundled @oai/artifact-tool runtime, not npm dependencies.
// First generate docs/event-registry.json with build_event_tracker.py.
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { Workbook, SpreadsheetFile } from '@oai/artifact-tool';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const data = JSON.parse(await fs.readFile(path.join(root, 'docs/event-registry.json'), 'utf8'));
const output = path.join(root, 'outputs/aura-clash-events');
const qa = path.join(root, 'output/event-tracker-qa');
await fs.mkdir(output, { recursive: true });
await fs.mkdir(qa, { recursive: true });
const wb = Workbook.create();

function sheet(name, title, columns, rows, widths, tableName) {
  const s = wb.worksheets.add(name);
  s.showGridLines = false;
  s.tabColor = '#563A68';
  const last = String.fromCharCode(64 + columns.length);
  const end = 5 + rows.length;
  const used = s.getRange(`A1:${last}${end}`);
  used.format.font = { name: 'Arial', size: 10, color: '#24212A' };
  used.format.verticalAlignment = 'center';
  s.getRange('A2').values = [[title]];
  s.getRange('A2').format.font = { name: 'Arial', size: 14, bold: true, color: '#382341' };
  s.getRange('A2').format.rowHeight = 24;
  s.getRange(`A3:${last}3`).format.borders = { bottom: { style: 'thin', color: '#B9AFBE' } };
  s.getRange('A3').values = [[`CK3 ${data.ck3_version} | ${data.events.length} modified events | ${data.options.length} added choices`]];
  s.getRange('A4').values = [['Sorted by content pack, event name, event ID. Filter the headers; dynamic names depend on the save.']];
  s.getRange('A3:A4').format.font = { name: 'Arial', size: 10, italic: true, color: '#655F69' };
  s.getRange(`A5:${last}${end}`).values = [columns, ...rows];
  const table = s.tables.add(`A5:${last}${end}`, true, tableName);
  table.style = 'TableStyleLight1';
  table.showFilterButton = true;
  s.getRange(`A5:${last}5`).format = {
    fill: '#563A68', font: { name: 'Arial', size: 10, bold: true, color: '#FFFFFF' },
    horizontalAlignment: 'center', verticalAlignment: 'center', wrapText: true, rowHeight: 30,
    borders: { insideVertical: { style: 'thin', color: '#FFFFFF' } },
  };
  widths.forEach((width, i) => {
    const col = String.fromCharCode(65 + i);
    s.getRange(`${col}5:${col}${end}`).format.columnWidth = width;
  });
  const body = s.getRange(`A6:${last}${end}`);
  body.format.wrapText = true;
  body.format.fill = '#FFFFFF';
  body.format.verticalAlignment = 'top';
  // Size each wrapped row to the actual longest cell, keeping full text visible.
  rows.forEach((row, i) => {
    const lines = Math.max(...row.map((value, j) => {
      const text = String(value ?? '');
      const words = text.split(/\s+/);
      let count = 1, used = 0;
      const capacity = Math.max(8, Math.floor(widths[j] * 0.94));
      for (const word of words) {
        if (used && used + word.length + 1 > capacity) { count++; used = 0; }
        count += Math.max(0, Math.ceil(word.length / capacity) - 1);
        used += word.length + 1;
      }
      return count;
    }));
    s.getRange(`A${i + 6}:${last}${i + 6}`).format.rowHeight = Math.max(32, lines * 14 + 8);
    if (i % 2 === 1) s.getRange(`A${i + 6}:${last}${i + 6}`).format.fill = '#F2EFF5';
  });
  s.freezePanes.freezeRows(5);
  s.freezePanes.freezeColumns(3);
  return s;
}

const events = sheet('Events', 'Aura Clash — modified events',
  ['Content pack', 'Event name', 'Event ID', 'Added choices', 'Change type', 'Vanilla source', 'Mod source'],
  data.events.map(r => [r.content_pack, r.event_name, r.event_id, r.added_choices, r.change_type, r.vanilla_source, r.mod_source]),
  [24, 36, 44, 13, 20, 72, 64], 'ModifiedEvents');
events.getRange(`D6:D${data.events.length + 5}`).setNumberFormat('0');
events.getRange(`D6:D${data.events.length + 5}`).format.horizontalAlignment = 'right';

sheet('Options', 'Aura Clash — added cultivation choices',
  ['Content pack', 'Event name', 'Event ID', 'Added option', 'Ability index', 'Outcome', 'Exertion', 'Option key', 'Vanilla source', 'Mod source'],
  data.options.map(r => [r.content_pack, r.event_name, r.event_id, r.added_option, r.ability_index, r.outcome, r.exertion, r.option_key, r.vanilla_source, r.mod_source]),
  [24, 36, 44, 60, 40, 84, 52, 60, 72, 64], 'CultivationOptions');

wb.recalculate();
console.log((await wb.inspect({ kind: 'sheet,table', maxChars: 2200, tableMaxRows: 2, tableMaxCols: 4 })).ndjson);
for (const name of ['Events', 'Options']) {
  const preview = await wb.render({ sheetName: name, range: name === 'Events' ? 'A1:E11' : 'D5:G10', scale: 1.2, format: 'png' });
  await fs.writeFile(path.join(qa, `${name.toLowerCase()}.png`), new Uint8Array(await preview.arrayBuffer()));
}
const xlsx = await SpreadsheetFile.exportXlsx(wb);
await xlsx.save(path.join(output, 'AuraClash-event-tracker.xlsx'));
console.log(`Exported ${data.events.length} events and ${data.options.length} options.`);
