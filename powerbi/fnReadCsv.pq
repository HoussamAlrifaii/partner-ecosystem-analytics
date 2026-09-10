// 📖 READ ONLY — shared file-loading function; name this query fnReadCsv.
(FileName as text, ColumnTypes as list) as table =>
let
    Source = Csv.Document(File.Contents(DataFolder & "/" & FileName),
        [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    // 🎯 INTERVIEW FOCUS — normalize missing values before explicit typing, never silently drop errors.
    Missing = Table.ReplaceValue(Headers, "", null, Replacer.ReplaceValue, Table.ColumnNames(Headers)),
    Typed = Table.TransformColumnTypes(Missing, ColumnTypes, "en-US")
in
    Typed
