const CONFIG = Object.freeze({
  SITE_URL: 'https://ahmed-alhafiz.github.io/',
  SUBJECT_PREFIX: '[GSC-AUTO]',
  PRIORITY_PAGE_FRAGMENTS: [
    '/books/umm-abbas/',
    '/books/sirou-fi-alard/'
  ],
  TOP_QUERY_PAGE_ROWS: 300,
  TOP_PAGE_ROWS: 100,
  MAX_API_PAGES: 4
});

/**
 * Main daily job.
 * Reads finalized Google Search Console data and emails a machine-readable
 * report to the Google account that owns/executes this Apps Script project.
 */
function runDailyGscReport() {
  const latestFinalDate = getLatestFinalDate_();
  if (!latestFinalDate) {
    throw new Error('No finalized Search Console date was returned.');
  }

  const currentEnd = latestFinalDate;
  const currentStart = offsetDateString_(currentEnd, -6);
  const previousEnd = offsetDateString_(currentStart, -1);
  const previousStart = offsetDateString_(previousEnd, -6);

  const currentQueryPage = queryAll_(currentStart, currentEnd, ['query', 'page']);
  const previousQueryPage = queryAll_(previousStart, previousEnd, ['query', 'page']);
  const currentPages = queryAll_(currentStart, currentEnd, ['page']);
  const previousPages = queryAll_(previousStart, previousEnd, ['page']);

  const report = {
    schemaVersion: 1,
    generatedAt: new Date().toISOString(),
    siteUrl: CONFIG.SITE_URL,
    dataState: 'final',
    periods: {
      current: { startDate: currentStart, endDate: currentEnd },
      previous: { startDate: previousStart, endDate: previousEnd }
    },
    current: {
      topQueryPage: topByImpressions_(currentQueryPage, CONFIG.TOP_QUERY_PAGE_ROWS),
      priorityQueryPage: priorityRows_(currentQueryPage),
      topPages: topByImpressions_(currentPages, CONFIG.TOP_PAGE_ROWS)
    },
    previous: {
      topQueryPage: topByImpressions_(previousQueryPage, CONFIG.TOP_QUERY_PAGE_ROWS),
      priorityQueryPage: priorityRows_(previousQueryPage),
      topPages: topByImpressions_(previousPages, CONFIG.TOP_PAGE_ROWS)
    },
    notes: [
      'Search Console API can omit some low-volume/anonymized query data.',
      'Use query+page rows for diagnosis and page totals as a supporting check.',
      'Do not treat average position as an isolated objective.'
    ]
  };

  const recipient = Session.getEffectiveUser().getEmail();
  if (!recipient) {
    throw new Error('Could not determine the effective Google account email.');
  }

  const subject = `${CONFIG.SUBJECT_PREFIX} Ahmed Alhafiz ${currentEnd}`;
  const body = [
    'Automated finalized Google Search Console report.',
    `Site: ${CONFIG.SITE_URL}`,
    `Current: ${currentStart} to ${currentEnd}`,
    `Previous: ${previousStart} to ${previousEnd}`,
    '',
    'GSC_AUTO_JSON_START',
    JSON.stringify(report),
    'GSC_AUTO_JSON_END'
  ].join('\n');

  MailApp.sendEmail({
    to: recipient,
    subject: subject,
    body: body,
    name: 'Ahmed Alhafiz GSC Relay'
  });
}

/**
 * One-time setup helper. Run manually once after creating the Apps Script.
 * It installs a daily trigger around 06:00 in the script timezone, then sends
 * an immediate test report so the end-to-end path can be verified.
 */
function setupGscRelay() {
  removeExistingReportTriggers_();
  ScriptApp.newTrigger('runDailyGscReport')
    .timeBased()
    .atHour(6)
    .everyDays(1)
    .create();

  runDailyGscReport();
}

function removeExistingReportTriggers_() {
  ScriptApp.getProjectTriggers().forEach(trigger => {
    if (trigger.getHandlerFunction() === 'runDailyGscReport') {
      ScriptApp.deleteTrigger(trigger);
    }
  });
}

/**
 * Finds the newest finalized date by asking Search Console for finalized daily
 * rows over a recent window. This avoids guessing the normal data lag.
 */
function getLatestFinalDate_() {
  const todayPt = Utilities.formatDate(new Date(), 'America/Los_Angeles', 'yyyy-MM-dd');
  const start = offsetDateString_(todayPt, -30);
  const end = offsetDateString_(todayPt, -1);
  const rows = queryAll_(start, end, ['date']);
  if (!rows.length) return null;
  return rows[rows.length - 1].keys[0];
}

function queryAll_(startDate, endDate, dimensions) {
  const endpoint = `https://www.googleapis.com/webmasters/v3/sites/${encodeURIComponent(CONFIG.SITE_URL)}/searchAnalytics/query`;
  const token = ScriptApp.getOAuthToken();
  const allRows = [];
  let startRow = 0;

  for (let page = 0; page < CONFIG.MAX_API_PAGES; page++) {
    const payload = {
      startDate: startDate,
      endDate: endDate,
      dimensions: dimensions,
      type: 'web',
      aggregationType: 'auto',
      rowLimit: 25000,
      startRow: startRow,
      dataState: 'final'
    };

    const response = UrlFetchApp.fetch(endpoint, {
      method: 'post',
      contentType: 'application/json',
      payload: JSON.stringify(payload),
      headers: { Authorization: `Bearer ${token}` },
      muteHttpExceptions: true
    });

    const status = response.getResponseCode();
    const text = response.getContentText();
    if (status < 200 || status >= 300) {
      throw new Error(`Search Console API ${status}: ${text}`);
    }

    const parsed = JSON.parse(text || '{}');
    const rows = (parsed.rows || []).map(row => ({
      keys: row.keys || [],
      clicks: Number(row.clicks || 0),
      impressions: Number(row.impressions || 0),
      ctr: Number(row.ctr || 0),
      position: Number(row.position || 0)
    }));

    allRows.push(...rows);
    if (rows.length < 25000) break;
    startRow += rows.length;
  }

  return allRows;
}

function topByImpressions_(rows, limit) {
  return rows
    .slice()
    .sort((a, b) => (b.impressions - a.impressions) || (b.clicks - a.clicks))
    .slice(0, limit);
}

function priorityRows_(rows) {
  return rows
    .filter(row => {
      const page = pageFromKeys_(row.keys);
      return CONFIG.PRIORITY_PAGE_FRAGMENTS.some(fragment => page.includes(fragment));
    })
    .sort((a, b) => (b.impressions - a.impressions) || (b.clicks - a.clicks));
}

function pageFromKeys_(keys) {
  const candidate = (keys || []).find(value => /^https?:\/\//i.test(String(value)));
  return candidate ? String(candidate) : '';
}

function offsetDateString_(dateString, deltaDays) {
  const parts = dateString.split('-').map(Number);
  const date = new Date(Date.UTC(parts[0], parts[1] - 1, parts[2], 12, 0, 0));
  date.setUTCDate(date.getUTCDate() + deltaDays);
  return Utilities.formatDate(date, 'UTC', 'yyyy-MM-dd');
}
