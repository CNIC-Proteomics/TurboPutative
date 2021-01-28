// Default values parameters of different modules
defaultValues = {
    
    Tagger: {
        halogenatedRegex: "([Ff]luor(?!ene)|[Cc]hlor(?!ophyl)|[Bb]rom|[Ii]od)",
        peptideRegex: "(?i)^(Ala|Arg|Asn|Asp|Cys|Gln|Glu|Gly|His|Ile|Leu|Lys|Met|Phe|Pro|Ser|Thr|Trp|Tyr|Val|[-\\s,]){3,}$",
    },

    REname: {
        removeRowRegex: "(?i)No compounds found for experimental mass",
        separator: "\\s//\\s",
        aaSeparator: "\\s",
    },

    RowMerger: {
        comparedCol: "Experimental mass, Adduct, mz Error (ppm), Molecular Weight",
        conservedCol: "Identifier, Name",
    },

    TableMerger: {
        decimalPlaces: "4",
    },
    
};