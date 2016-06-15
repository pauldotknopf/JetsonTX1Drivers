// Copyright (c) 2009-2015 Quadralay Corporation.  All rights reserved.
//
// Validated with JSLint <http://www.jslint.com/>
//

/*jslint white: true, maxerr: 50, indent: 4 */
/*global UnicodeInfo */

var Unicode = {};

Unicode.Break_CheckBreak_Sequence = function (ParamPrevious, ParamCurrent)
{
  'use strict';

  var  VarResult = true;

  if (
      (
       (ParamPrevious === ' ')
      )
       &&
      (
       (true)
      )
     )
  {
    VarResult = false;
  }
  else if (
           (
            (true)
           )
            &&
           (
            (UnicodeInfo.WWNoBreak(ParamCurrent))
           )
          )
  {
    VarResult = false;
  }
  else if (
           (
            (UnicodeInfo.WWNoBreak(ParamPrevious))
           )
            &&
           (
            (true)
           )
          )
  {
    VarResult = false;
  }
  else if (
           (
            (UnicodeInfo.Korean_L(ParamPrevious))
           )
            &&
           (
            (UnicodeInfo.Korean_L(ParamCurrent))
           )
          )
  {
    VarResult = false;
  }
  else if (
           (
            (UnicodeInfo.Korean_L(ParamPrevious))
             ||
            (UnicodeInfo.Korean_LV(ParamPrevious))
           )
            &&
           (
            (UnicodeInfo.Korean_LV(ParamCurrent))
           )
          )
  {
    VarResult = false;
  }
  else if (
           (
            (UnicodeInfo.Korean_L(ParamPrevious))
             ||
            (UnicodeInfo.Korean_LV(ParamPrevious))
           )
            &&
           (
            (UnicodeInfo.Korean_V(ParamCurrent))
           )
          )
  {
    VarResult = false;
  }
  else if (
           (
            (UnicodeInfo.Korean_L(ParamPrevious))
           )
            &&
           (
            (UnicodeInfo.Korean_LVT(ParamCurrent))
           )
          )
  {
    VarResult = false;
  }
  else if (
           (
            (UnicodeInfo.Korean_L(ParamPrevious))
             ||
            (UnicodeInfo.Korean_LV(ParamPrevious))
             ||
            (UnicodeInfo.Korean_V(ParamPrevious))
             ||
            (UnicodeInfo.Korean_LVT(ParamPrevious))
             ||
            (UnicodeInfo.Korean_T(ParamPrevious))
           )
            &&
           (
            (UnicodeInfo.Korean_T(ParamCurrent))
           )
          )
  {
    VarResult = false;
  }
  else if (
           (
            (UnicodeInfo.ALetter(ParamPrevious))
             ||
            (UnicodeInfo.ABaseLetter(ParamPrevious))
             ||
            (UnicodeInfo.ACMLetter(ParamPrevious))
             ||
            (UnicodeInfo.Numeric(ParamPrevious))
             ||
            (UnicodeInfo.MidNum(ParamPrevious))
             ||
            (UnicodeInfo.MidNumLet(ParamPrevious))
             ||
            (UnicodeInfo.MidLetter(ParamPrevious))
             ||
            (UnicodeInfo.Katakana(ParamPrevious))
             ||
            (UnicodeInfo.Hiragana(ParamPrevious))
             ||
            (UnicodeInfo.Ideographic(ParamPrevious))
             ||
            (UnicodeInfo.Korean_L(ParamPrevious))
             ||
            (UnicodeInfo.Korean_LV(ParamPrevious))
             ||
            (UnicodeInfo.Korean_V(ParamPrevious))
             ||
            (UnicodeInfo.Korean_LVT(ParamPrevious))
             ||
            (UnicodeInfo.Korean_T(ParamPrevious))
             ||
            (UnicodeInfo.Extend(ParamPrevious))
           )
            &&
           (
            (UnicodeInfo.Extend(ParamCurrent))
           )
          )
  {
    VarResult = false;
  }
  else if (
           (
            (UnicodeInfo.ALetter(ParamPrevious))
             ||
            (UnicodeInfo.Extend(ParamPrevious))
           )
            &&
           (
            (UnicodeInfo.ALetter(ParamCurrent))
           )
          )
  {
    VarResult = false;
  }
  else if (
           (
            (UnicodeInfo.Katakana(ParamPrevious))
           )
            &&
           (
            (UnicodeInfo.Katakana(ParamCurrent))
           )
          )
  {
    VarResult = false;
  }
  else if (
           (
            (UnicodeInfo.Numeric(ParamPrevious))
             ||
            (UnicodeInfo.MidNumLet(ParamPrevious))
             ||
            (UnicodeInfo.MidLetter(ParamPrevious))
             ||
            (UnicodeInfo.Extend(ParamPrevious))
           )
            &&
           (
            (UnicodeInfo.ABaseLetter(ParamCurrent))
             ||
            (UnicodeInfo.ACMLetter(ParamCurrent))
           )
          )
  {
    VarResult = false;
  }
  else if (
           (
            (UnicodeInfo.ALetter(ParamPrevious))
             ||
            (UnicodeInfo.ABaseLetter(ParamPrevious))
             ||
            (UnicodeInfo.ACMLetter(ParamPrevious))
             ||
            (UnicodeInfo.Extend(ParamPrevious))
           )
            &&
           (
            (UnicodeInfo.MidNumLet(ParamCurrent))
             ||
            (UnicodeInfo.MidLetter(ParamCurrent))
           )
          )
  {
    VarResult = false;
  }
  else if (
           (
            (UnicodeInfo.ABaseLetter(ParamPrevious))
             ||
            (UnicodeInfo.ACMLetter(ParamPrevious))
             ||
            (UnicodeInfo.MidNum(ParamPrevious))
             ||
            (UnicodeInfo.MidNumLet(ParamPrevious))
             ||
            (UnicodeInfo.Numeric(ParamPrevious))
             ||
            (UnicodeInfo.Extend(ParamPrevious))
           )
            &&
           (
            (UnicodeInfo.Numeric(ParamCurrent))
           )
          )
  {
    VarResult = false;
  }
  else if (
           (
            (UnicodeInfo.Numeric(ParamPrevious))
             ||
            (UnicodeInfo.Extend(ParamPrevious))
           )
            &&
           (
            (UnicodeInfo.MidNum(ParamCurrent))
             ||
            (UnicodeInfo.MidNumLet(ParamCurrent))
           )
          )
  {
    VarResult = false;
  }
  else if (
           (
            (true)
           )
            &&
           (
            (UnicodeInfo.Hiragana(ParamCurrent))
             ||
            (UnicodeInfo.Ideographic(ParamCurrent))
           )
          )
  {
    VarResult = true;
  }
  else if (
           (
            (true)
           )
            &&
           (
            (UnicodeInfo.WWCloseBracket(ParamCurrent))
           )
          )
  {
    VarResult = false;
  }
  else if (
           (
            (UnicodeInfo.WWOpenBracket(ParamPrevious))
           )
            &&
           (
            (true)
           )
          )
  {
    VarResult = false;
  }

  return VarResult;
};

Unicode.CheckBreakAtIndex = function (ParamString, ParamIndex)
{
  'use strict';

  var  VarResult, VarPrevious, VarCurrent, VarNext;

  VarResult = false;

  if (ParamIndex < ParamString.length)
  {
    if (ParamString.length === 1)
    {
      VarResult = false;
    }
    else if (ParamString.length > 1)
    {
      // String is at least two characters long
      //
      if (ParamIndex === 0)
      {
        VarResult = false;
      }
      else
      {
        VarPrevious = ParamString.charAt(ParamIndex - 1);
        VarCurrent = ParamString.charAt(ParamIndex);

        VarResult = Unicode.Break_CheckBreak_Sequence(VarPrevious, VarCurrent);

        // Check ending
        //
        if ( ! VarResult)
        {
          // Ending with a middle character?
          //
          if (
              (UnicodeInfo.MidLetter(VarCurrent))
               ||
              (UnicodeInfo.MidNumLet(VarCurrent))
               ||
              (UnicodeInfo.MidNum(VarCurrent))
             )
          {
            // Check next character
            //
            if ((ParamIndex + 1) === ParamString.length)
            {
              // Break at end of search string
              //
              VarResult = true;
            }
            else
            {
              VarNext = ParamString.charAt(ParamIndex + 1);

              // Depends on the next character
              //
              VarResult = Unicode.Break_CheckBreak_Sequence(VarCurrent, VarNext);
            }
          }
        }
      }
    }
  }

  return VarResult;
};
