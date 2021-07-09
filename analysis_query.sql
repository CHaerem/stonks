SELECT dividend_history.ticker, DATE(dividend_history.ex_date), dividend_history.dividends_paid, 
before_ex.close as close_before_ex, on_ex.close as close_on_ex,  
(on_ex.close  + dividend_history.dividends_paid - before_ex.close) AS potential_gain
FROM dividend_history
INNER JOIN daily_price  as  before_ex ON DATE(dividend_history.ex_date, "-1 day") = before_ex.date AND dividend_history.ticker = rtrim(before_ex.ticker, ".OL")
INNER JOIN daily_price  as  on_ex ON DATE(dividend_history.ex_date) = on_ex.date AND dividend_history.ticker = rtrim(on_ex.ticker, ".OL")
WHERE potential_gain > 0
ORDER BY dividend_history.ex_date DESC