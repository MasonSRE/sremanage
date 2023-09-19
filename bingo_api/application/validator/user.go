package validator

import (
	. "bingo_api/application/model"
	. "bingo_api/application/utils"
	"errors"
	"github.com/go-playground/validator/v10"
)

/**
登录验证器
*/

func UserValidator(user *User) error {
	validate, trans := GenValidate()
	err := validate.Struct(user)
	if err != nil {
		for _, err := range err.(validator.ValidationErrors) {
			return errors.New(err.Translate(trans))
		}
	}
	return nil
}
