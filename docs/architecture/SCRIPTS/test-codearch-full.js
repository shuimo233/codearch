#!/usr/bin/env node
/**
 * CodeArch Skill - Comprehensive E2E Test
 * =========================================
 * Tests the architecture.html viewer using Playwright.
 * Can be run standalone or integrated with Cursor agent.
 * 
 * Usage:
 *   node test-codearch-full.js [path-to-architecture.html] [--headless]
 *   
 * Agent Integration:
 *   This script outputs JSON results that can be parsed by the agent
 *   to determine next steps in fixing issues.
 */

const { chromium } = require('playwright');
const http = require('http');
const fs = require('fs');
const path = require('path');

const DEFAULT_HTML_PATH = process.argv[2] || path.join(__dirname, '..', 'architecture', 'TEMPLATES', 'architecture.html');
const PORT = 9876;
const OUTPUT_JSON = process.argv.includes('--json');

let server;
let browser;

function startServer(htmlPath) {
    return new Promise((resolve, reject) => {
        let htmlContent = fs.readFileSync(htmlPath, 'utf-8');

        server = http.createServer((req, res) => {
            res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
            res.end(htmlContent);
        });
        
        server.listen(PORT, () => resolve(server.address().port));
        server.on('error', reject);
    });
}

function stopServer() {
    return new Promise((resolve) => {
        if (server) server.close(() => resolve());
        else resolve();
    });
}

function log(msg, isError = false) {
    if (OUTPUT_JSON) return;
    console.log(isError ? `❌ ${msg}` : `✅ ${msg}`);
}

function logInfo(msg) {
    if (OUTPUT_JSON) return;
    console.log(`ℹ️  ${msg}`);
}

// ========== TEST FUNCTIONS ==========

async function testPageLoads(page) {
    const errors = [];
    page.on('pageerror', (err) => errors.push(err.message));
    page.on('console', (msg) => {
        if (msg.type() === 'error') errors.push(msg.text());
    });
    
    await page.goto(`http://localhost:${PORT}`);
    await page.waitForLoadState('domcontentloaded');
    
    // Wait for render
    await page.waitForTimeout(2000);
    
    return { passed: errors.length === 0, errors };
}

async function testProjectInfo(page) {
    try {
        const info = await page.$eval('#projectInfo', el => el.innerHTML);
        return { 
            passed: info.length > 0, 
            data: info 
        };
    } catch (e) {
        return { passed: false, error: e.message };
    }
}

async function testComponentTree(page) {
    try {
        const nodes = await page.$$('.tree-node');
        const groups = await page.$$('.layer-group');
        
        // Check if components are actually visible
        const visibleNodes = await page.$$eval('.tree-node', nodes => 
            nodes.filter(n => getComputedStyle(n).display !== 'none').length
        );
        
        return { 
            passed: visibleNodes > 0, 
            totalNodes: nodes.length,
            visibleNodes,
            layerGroups: groups.length
        };
    } catch (e) {
        return { passed: false, error: e.message };
    }
}

async function testArchView(page) {
    try {
        // Check layer view has arch-nodes
        const nodes = await page.$$('#layerView .arch-node');
        const layers = await page.$$('#layerView .arch-layer');
        // Check SVG connections overlay exists
        const svg = await page.$('#connectionsSVG');

        return {
            passed: nodes.length > 0 && layers.length > 0 && !!svg,
            nodeCount: nodes.length,
            layerCount: layers.length,
            hasConnections: !!svg
        };
    } catch (e) {
        return { passed: false, error: e.message };
    }
}

async function testDomainFilter(page) {
    try {
        const tags = await page.$$('.domain-filter .filter-tag');
        if (tags.length === 0) return { passed: false, error: 'No filter tags' };
        
        // Click first domain filter
        await tags[1].click();
        await page.waitForTimeout(500);
        
        return { passed: true, filterCount: tags.length };
    } catch (e) {
        return { passed: false, error: e.message };
    }
}

async function testComponentClick(page) {
    try {
        const node = await page.$('.tree-node');
        if (!node) return { passed: false, error: 'No tree node' };
        
        await node.click();
        await page.waitForTimeout(500);
        
        const detail = await page.$('.detail-header h3');
        if (!detail) return { passed: false, error: 'Detail not shown' };
        
        const text = await detail.textContent();
        return { passed: true, componentId: text };
    } catch (e) {
        return { passed: false, error: e.message };
    }
}

async function testThemeToggle(page) {
    try {
        const btn = await page.$('#themeToggle');
        if (!btn) return { passed: false, error: 'Theme button not found' };
        
        const initial = await page.$eval('html', el => el.getAttribute('data-theme') || 'light');
        await btn.click();
        await page.waitForTimeout(300);
        
        const after = await page.$eval('html', el => el.getAttribute('data-theme'));
        
        return { passed: initial !== after, initialTheme: initial, newTheme: after };
    } catch (e) {
        return { passed: false, error: e.message };
    }
}

async function testTabSwitching(page) {
    try {
        // Test layer/flow tabs
        const canvasTabs = await page.$$('.tab-bar .tab-btn');
        for (const tab of canvasTabs) {
            await tab.click();
            await page.waitForTimeout(1000);
        }
        
        return { passed: canvasTabs.length >= 2 };
    } catch (e) {
        return { passed: false, error: e.message };
    }
}

async function testSearch(page) {
    try {
        const input = await page.$('#searchInput');
        if (!input) return { passed: false, error: 'Search input not found' };
        
        await input.fill('Product');
        await page.waitForTimeout(500);
        
        return { passed: true };
    } catch (e) {
        return { passed: false, error: e.message };
    }
}

async function testZoomControls(page) {
    try {
        const zoomIn = await page.$('.zoom-btn:first-of-type');
        const zoomLevel = await page.$('#zoomLevel');
        
        if (!zoomIn || !zoomLevel) return { passed: false, error: 'Zoom controls missing' };
        
        const before = await zoomLevel.textContent();
        await zoomIn.click();
        await page.waitForTimeout(200);
        const after = await zoomLevel.textContent();
        
        return { passed: before !== after, before, after };
    } catch (e) {
        return { passed: false, error: e.message };
    }
}

async function testSystemDataIntegrity(page) {
    try {
        const data = await page.evaluate(() => {
            try {
                return {
                    hasSystemData: typeof systemData !== 'undefined',
                    componentCount: systemData?.components?.length || 0,
                    dependencyCount: systemData?.dependencies?.length || 0,
                    externalServiceCount: systemData?.externalServices?.length || 0,
                    hasMeta: !!systemData?.meta,
                    hasDomains: !!systemData?.domains,
                    metaNodeCount: systemData?.meta?.nodeCount || 0
                };
            } catch (e) {
                return { error: e.message };
            }
        });
        
        // Check if nodeCount matches
        const countMatch = data.componentCount === data.metaNodeCount;
        
        return { 
            passed: data.hasSystemData && data.componentCount > 0 && countMatch,
            ...data,
            countMatch
        };
    } catch (e) {
        return { passed: false, error: e.message };
    }
}

// ========== MAIN TEST RUNNER ==========

async function runTests(htmlPath) {
    const results = {
        timestamp: new Date().toISOString(),
        htmlPath,
        tests: {}
    };
    
    try {
        logInfo(`Starting server on port ${PORT}...`);
        await startServer(htmlPath);
        
        logInfo('Launching browser...');
        browser = await chromium.launch({ headless: true });
        const page = await browser.newPage();
        
        // Run tests
        const tests = [
            { name: 'page_loads', fn: testPageLoads },
            { name: 'system_data_integrity', fn: testSystemDataIntegrity },
            { name: 'project_info', fn: testProjectInfo },
            { name: 'component_tree', fn: testComponentTree },
            { name: 'arch_view', fn: testArchView },
            { name: 'domain_filter', fn: testDomainFilter },
            { name: 'component_click', fn: testComponentClick },
            { name: 'theme_toggle', fn: testThemeToggle },
            { name: 'tab_switching', fn: testTabSwitching },
            { name: 'search', fn: testSearch },
            { name: 'zoom_controls', fn: testZoomControls },
        ];
        
        for (const test of tests) {
            try {
                results.tests[test.name] = await test.fn(page);
            } catch (e) {
                results.tests[test.name] = { passed: false, error: e.message };
            }
        }
        
    } catch (e) {
        results.fatalError = e.message;
    } finally {
        if (browser) await browser.close();
        await stopServer();
    }
    
    // Calculate summary
    const testResults = Object.values(results.tests);
    results.summary = {
        total: testResults.length,
        passed: testResults.filter(t => t.passed).length,
        failed: testResults.filter(t => !t.passed).length
    };
    results.success = results.summary.failed === 0 && !results.fatalError;
    
    return results;
}

// Entry point
const htmlPath = process.argv[2] || DEFAULT_HTML_PATH;

if (!fs.existsSync(htmlPath)) {
    const error = { error: `HTML file not found: ${htmlPath}` };
    if (OUTPUT_JSON) {
        console.log(JSON.stringify(error));
    } else {
        console.error(`❌ Error: HTML file not found: ${htmlPath}`);
        console.error('Usage: node test-codearch-full.js [path-to-architecture.html] [--json]');
    }
    process.exit(1);
}

runTests(htmlPath).then(results => {
    if (OUTPUT_JSON) {
        console.log(JSON.stringify(results, null, 2));
    } else {
        console.log('\n' + '='.repeat(50));
        console.log('CodeArch E2E Test Results');
        console.log('='.repeat(50));
        console.log(`\nTested: ${results.htmlPath}`);
        console.log(`\nSummary: ${results.summary.passed}/${results.summary.total} passed`);
        
        console.log('\nDetailed Results:');
        for (const [name, result] of Object.entries(results.tests)) {
            console.log(`  ${result.passed ? '✅' : '❌'} ${name}`);
            if (result.error) console.log(`     Error: ${result.error}`);
            if (result.nodeCount) console.log(`     Nodes: ${result.nodeCount}, Edges: ${result.edgeCount}`);
            if (result.componentCount) console.log(`     Components: ${result.componentCount}`);
        }
        
        console.log('\n' + '='.repeat(50));
        if (results.success) {
            console.log('🎉 All tests passed!');
        } else {
            console.log('⚠️  Some tests failed - review the output above');
        }
        console.log('='.repeat(50));
    }
    
    process.exit(results.success ? 0 : 1);
}).catch(err => {
    console.error('Fatal error:', err);
    process.exit(1);
});
