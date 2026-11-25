@echo off
title ThesisForge AI — Run Automated Tests
echo ========================================================
echo   Running ThesisForge AI Automated Test Suite (38 Tests)...
echo   - API Endpoints (Health, Assets, Runs, Trace, Evidence, Signals, Coverage, Market Data)
echo   - 12-Category Document Package Tracking & Company-Specific Isolation
echo   - 5-Year Historical OHLCV Market Data Ingestion & Technical Indicators
echo   - Timeframe Stop Loss & Target Pricing (Intraday, Swing, Positional)
echo   - Risk:Reward Ratio Calculation Constraints & Position Sizing
echo   - Insufficient Market Data Fallback Safeguards (< 14 bars)
echo   - RAG, Evidence Extraction and Citation Validation
echo   - 1-Turn Rebuttal and Risk Veto Safety Threshold
echo   - Cryptographic SHA-256 Hash Chaining
echo   - Q18 Scenarios A, B, and C
echo   - Stock Universe (12 Real Stocks + 3 Benchmarks)
echo   - Strict Anti-Fabrication Guarantees (HOLD with INSUFFICIENT_EVIDENCE)
echo   - Derivatives Joint Price / OI Buildup Engine
echo   - Ten Methodology-Inspired Review Personas
echo   - Historical Replay Evaluation & Expectancy Metrics
echo ========================================================

set PATH=C:\Users\91860\AppData\Local\Programs\Python\Python313;C:\Users\91860\AppData\Local\Programs\Python\Python313\Scripts;%PATH%

cd /d "%~dp0"

pytest -v

echo.
echo ========================================================
echo   Tests Complete! Press any key to close this window.
echo ========================================================
pause
