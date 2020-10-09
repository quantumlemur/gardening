import React, { useState } from "react";

import "gestalt/dist/gestalt.css";
import { Box, TextField } from "gestalt";

function ManagementElement({
  varName,
  value,
  placeholder,
  updateValue,
  disabled,
  label,
  date,
  helperText,
  allowedType,
}) {
  const [data, setData] = useState(value);
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
    const target = event.event.target;

    if (allowedType) {
      if (typeCheckRegexes[allowedType].test(target.value)) {
        setErrorMessage("");

        updateValue(varName, target.value);
      } else {
        setErrorMessage(typeCheckErrors[allowedType]);
      }
    }

    setData(target.value);
  }

  return (
    <Box flex="grow" paddingX={3} paddingY={3}>
      <TextField
        key={varName}
        id={varName}
        label={label ? label : varName}
        name={varName}
        value={date ? new Date(data * 1000).toString() : data.toString()}
        helperText={helperText}
        onChange={handleInputChange}
        placeholder={placeholder ? placeholder : varName}
        disabled={disabled}
        errorMessage={errorMessage}
      />
    </Box>
  );
}

export default ManagementElement;
