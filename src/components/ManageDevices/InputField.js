import React, { useState } from "react";

import "gestalt/dist/gestalt.css";
import { Box, TextField } from "gestalt";

function InputField({
  varName,
  value,
  placeholder,
  type,
  disabled,
  label,
  date,
  helperText,
  allowedType,
  onChange,
}) {
  // const [data, setData] = useState(value);
  const [errorMessage, setErrorMessage] = useState("");

  const typeCheckRegexes = {
    positiveInt: /^\d+$/,
    bool: /^[01]$/,
  };

  const typeCheckErrors = {
    positiveInt: "Must be positive int",
    bool: "Must be 0 or 1",
  };

  function handleInputChange(event) {
    // const target = event.event.target;
    // console.log(target.id);
    // console.log(target.value);
    //
    // if (allowedType) {
    //   if (typeCheckRegexes[allowedType].test(target.value)) {
    //     setErrorMessage("");
    //
    //     updateValue(varName, target.value);
    //   } else {
    //     setErrorMessage(typeCheckErrors[allowedType]);
    //   }
    // } else {
    //   updateValue(varName, target.value);
    // }
    //
    // setData(target.value);
  }
  // console.log("management element render");

  return (
    <Box flex="grow" padding={3}>
      <TextField
        key={varName}
        id={varName}
        label={label ? label : varName}
        name={varName}
        value={value}
        helperText={helperText}
        onChange={(e) => onChange(e.event)}
        placeholder={placeholder ? placeholder : varName}
        disabled={disabled}
        errorMessage={errorMessage}
        type={type}
      />
    </Box>
  );
}

export default InputField;
