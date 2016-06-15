// Copyright (c) 2011-2015 Quadralay Corporation.  All rights reserved.
//
// ePublisher 2015.1
//
// Validated with JSLint <http://www.jslint.com/>
//

/*jslint maxerr: 50, indent: 4 */
/*global Unicode */

var SearchClient = {};

SearchClient.SearchReplace = function (paramString, paramSearchString, paramReplaceString) {
    'use strict';

    var  result, index;

    result = paramString;

    if ((paramSearchString.length > 0) && (result.length > 0)) {
        index = result.indexOf(paramSearchString, 0);
        while (index !== -1) {
            result = result.substring(0, index) + paramReplaceString + result.substring(index + paramSearchString.length, result.length);
            index += paramReplaceString.length;

            index = result.indexOf(paramSearchString, index);
        }
    }

    return result;
};

SearchClient.EscapeRegExg = function (param_string) {
    'use strict';

    var result;

    // Initialize result
    //
    result = param_string;

    // Escape special characters
    // \ . ? + - ^ $ | ( ) [ ] { }
    //
    result = SearchClient.SearchReplace(result, '\\', '\\\\');
    result = SearchClient.SearchReplace(result, '.', '\\.');
    result = SearchClient.SearchReplace(result, '?', '\\?');
    result = SearchClient.SearchReplace(result, '+', '\\+');
    result = SearchClient.SearchReplace(result, '-', '\\-');
    result = SearchClient.SearchReplace(result, '^', '\\^');
    result = SearchClient.SearchReplace(result, '$', '\\$');
    result = SearchClient.SearchReplace(result, '|', '\\|');
    result = SearchClient.SearchReplace(result, '(', '\\(');
    result = SearchClient.SearchReplace(result, ')', '\\)');
    result = SearchClient.SearchReplace(result, '[', '\\[');
    result = SearchClient.SearchReplace(result, ']', '\\]');
    result = SearchClient.SearchReplace(result, '{', '\\{');
    result = SearchClient.SearchReplace(result, '}', '\\}');

    // Windows IE 4.0 is brain dead
    //
    result = SearchClient.SearchReplace(result, '/', '[/]');

    // Convert * to .*
    //
    result = SearchClient.SearchReplace(result, '*', '.*');

    return result;
};

SearchClient.WordToRegExpPattern = function (paramWord) {
    'use strict';

    var result;

    // Escape special characters
    // Convert * to .*
    //
    result = SearchClient.EscapeRegExg(paramWord);

    // Add ^ and $ to force whole string match
    //
    result = '^' + result + '$';

    return result;
};

SearchClient.EscapeHTML = function (paramHTML) {
    'use strict';

    var  escapedHTML = paramHTML;

    // Escape problematic characters
    // & < > "
    //
    escapedHTML = SearchClient.SearchReplace(escapedHTML, '&', '&amp;');
    escapedHTML = SearchClient.SearchReplace(escapedHTML, '<', '&lt;');
    escapedHTML = SearchClient.SearchReplace(escapedHTML, '>', '&gt;');
    escapedHTML = SearchClient.SearchReplace(escapedHTML, '"', '&quot;');

    return escapedHTML;
};

SearchClient.ParseWordsAndPhrases = function (paramInput) {
    'use strict';

    var wordSplits, results, stringWithSpace, currentPhrase, currentWord, wordIndex, startQuotes;

    wordSplits = [];
    results = [];
    stringWithSpace = 'x x';
    currentPhrase = '';
    currentWord = '';
    wordIndex = 0;
    startQuotes = false;

    if (paramInput.length > 0) {
        wordSplits = paramInput.split(stringWithSpace.substring(1, 2));
        for (wordIndex = 0; wordIndex < wordSplits.length; wordIndex += 1) {
            currentWord = wordSplits[wordIndex];
            if (currentWord.length > 0) {
                // If the current word does not start with or end with a double quote
                // and a phrase has not been started, then add it to the result word list
                // and continue
                //
                if (currentWord.charAt(0) === '"') {
                    if (startQuotes) {
                        // This entry ends the current phrase and the word following
                        // the quote will be added as a separate word, unless there is
                        // a second quote at the start that will start a new phrase
                        //
                        results[results.length] = currentPhrase.substring(0, currentPhrase.length - 1);
                        currentPhrase = '';

                        while ((currentWord.length > 0) && (currentWord.charAt(0) === '"')) {
                            currentWord = currentWord.substring(1, currentWord.length);
                        }
                        if (currentWord.length > 0) {
                            currentPhrase += currentWord + ' ';
                        }
                    } else {
                        startQuotes = true;

                        // Strip off the leading quotes and process the word
                        //
                        while ((currentWord.length > 0) && (currentWord.charAt(0) === '"')) {
                            currentWord = currentWord.substring(1, currentWord.length);
                        }

                        if (currentWord.length > 0) {
                            // One Word Phrase - Add it as a word and set startQuotes to false
                            //
                            if (currentWord.charAt(currentWord.length - 1) === '"') {
                                startQuotes = false;
                                // Strip off trailing quotes and add it as a word
                                //
                                while ((currentWord.length > 0) && (currentWord.charAt(currentWord.length - 1) === '"')) {
                                    currentWord = currentWord.substring(0, currentWord.length - 1);
                                }

                                // Add the Word to the result array
                                //
                                results[results.length] = currentWord;
                            } else {
                                // The current word starts a phrase
                                //
                                currentPhrase += currentWord + ' ';
                            }
                        }
                    }
                } else if (currentWord.charAt(currentWord.length - 1) === '"') {
                    // Strip off trailing quotes regardless
                    //
                    while ((currentWord.length > 0) && (currentWord.charAt(currentWord.length - 1) === '"')) {
                        currentWord = currentWord.substring(0, currentWord.length - 1);
                    }

                    // Only process the word if the length is greater than 0 after
                    // stripping the trailing quotes
                    //
                    if (currentWord.length > 0) {
                        if (startQuotes) {
                            currentPhrase += currentWord;

                            results[results.length] = currentPhrase;
                            startQuotes = false;
                            currentPhrase = '';
                        } else {
                            // The phrase is not started
                            //
                            results[results.length] = currentWord;
                        }
                    }
                } else {
                    // The word is either a single word or in the middle of a phrase
                    //
                    if (startQuotes) {
                        currentPhrase += currentWord + ' ';
                    } else {
                        results[results.length] = currentWord;
                    }
                }
            }
        }
    }

    return results;
};

SearchClient.ApplyWordBreaks = function (paramString) {
    'use strict';

    var result, index, insert_break;

    result = '';

    // Apply Unicode rules for word breaking
    // These rules taken from http://www.unicode.org/unicode/reports/tr29/
    //
    for (index = 0; index < paramString.length; index += 1) {
        // Break?
        //
        insert_break = Unicode.CheckBreakAtIndex(paramString, index);
        if (insert_break) {
            result += ' ' + paramString.charAt(index);
        } else {
            result += paramString.charAt(index);
        }
    }

    return result;
};

SearchClient.SearchQueryToExpressions = function (param_search_query) {
    'use strict';

    var result, prefix_expression, suffix_expression, words_and_phrases, index, word_or_phrase, expression;

    result = [];
    prefix_expression = '[\u201C\u201D\u0022\u0027\u2018\u2019]?';
    suffix_expression = '[\\?\\.,:\u201C\u201D\u0022\u0027\u2018\u2019]?';
    if (param_search_query !== undefined) {
        words_and_phrases = SearchClient.ParseWordsAndPhrases(param_search_query);
        for (index = 0; index < words_and_phrases.length; index += 1) {
            word_or_phrase = words_and_phrases[index];

            // Avoid highlighting everything
            //
            if (word_or_phrase !== '*') {
                expression = SearchClient.EscapeRegExg(word_or_phrase);
                expression = SearchClient.SearchReplace(expression, '.*', '\\S*');
                expression = prefix_expression + expression + suffix_expression;
                result.push(expression);
            }
        }
    }

    return result;
};

SearchClient.ParseSearchWords = function (paramSearchWordsString, paramMinimumWordLength, paramStopWords) {
    'use strict';

    var result_words, preliminary_phrases, wordsAndPhrases, wordsAndPhrasesIndex, wordOrPhrase, words, wordsIndex, word, result_phrases, phraseIndex, preliminary_phrase, result;

    result_words = [];
    preliminary_phrases = [];

    // Add search words to hash
    //
    wordsAndPhrases = SearchClient.ParseWordsAndPhrases(paramSearchWordsString);
    for (wordsAndPhrasesIndex = 0; wordsAndPhrasesIndex < wordsAndPhrases.length; wordsAndPhrasesIndex += 1) {
        wordOrPhrase = SearchClient.ApplyWordBreaks(wordsAndPhrases[wordsAndPhrasesIndex]);
        words = SearchClient.ParseWordsAndPhrases(wordOrPhrase);

        // Phrase?
        //
        if (words.length > 1) {
            preliminary_phrases[preliminary_phrases.length] = [];
        }

        // Process words
        //
        for (wordsIndex = 0; wordsIndex < words.length; wordsIndex += 1) {
            word = words[wordsIndex];

            // Skip words below the minimum word length
            //
            if ((word.length > 0) && ((word.length >= paramMinimumWordLength) || (word.indexOf('*') >= 0))) {
                // Skip stop words
                //
                if (paramStopWords[word] === undefined) {
                    // Add to search words list
                    //
                    result_words.push(word);

                    // Add to phrase words list (if necessary)
                    //
                    if (words.length > 1) {
                        preliminary_phrases[preliminary_phrases.length - 1].push(word);
                    }
                }
            }
        }
    }

    // Ensure all phrases contain multiple words
    //
    result_phrases = []
    for (phraseIndex = 0; phraseIndex < preliminary_phrases.length; phraseIndex += 1) {
        preliminary_phrase = preliminary_phrases[phraseIndex];

        if (preliminary_phrase.length > 1) {
            result_phrases.push(preliminary_phrase);
        }
    }

    result = { 'words': result_words, 'phrases': result_phrases };

    return result;
};

SearchClient.ComparePageWithScore = function (param_alpha, param_beta) {
    'use strict';

    var result = 0;

    if (param_alpha.score < param_beta.score) {
        result = 1;
    } else if (param_alpha.score > param_beta.score) {
        result = -1;
    }

    return result;
};
