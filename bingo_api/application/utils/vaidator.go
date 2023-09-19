package utils

import (
	"github.com/go-playground/locales/zh"
	ut "github.com/go-playground/universal-translator"
	"github.com/go-playground/validator/v10"
	. "github.com/go-playground/validator/v10/translations/zh"
	"reflect"
)

/**
生成验证器
*/

func GenValidate() (*validator.Validate, ut.Translator) {
	zhCh := zh.New()
	validate := validator.New()
	//注册一个函数，获取struct tag里自定义的label作为字段名
	validate.RegisterTagNameFunc(func(fld reflect.StructField) string {
		name := fld.Tag.Get("label")
		return name
	})

	UniversalTranslator := ut.New(zhCh)
	trans, _ := UniversalTranslator.GetTranslator("zh")
	_ = RegisterDefaultTranslations(validate, trans)
	return validate, trans
}
